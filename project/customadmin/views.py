# pylint: disable=R0801,R0914,W0613,W0621
"""
Views for the CustomAdmin application.

This module contains views for listing, creating, editing, and deleting CustomAdmin.
"""
import re
import csv
import calendar
import zoneinfo
from collections import defaultdict
from datetime import datetime,timedelta
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import Group
from django.http import JsonResponse,HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import permission_required
from django.contrib.flatpages.models import FlatPage
from django.utils.html import strip_tags
from django.db.models import Sum,Count
from django.db.models.functions import TruncMonth,TruncDate

from project.users.models import User # pylint: disable=E0401
from project.product.models import Category,Product # pylint: disable=E0401
from project.order.models import Order # pylint: disable=E0401
from project.coupon.models import Coupon # pylint: disable=E0401
from project.utils import custom_required # pylint: disable=E0401
from .models import Banner,ContactUs,EmailTemplate,NewsletterSubscriber
from .tasks import celery_mail,send_contact_email
from .forms import (
    BannerForm,
    CustomFlatPageForm,
    EmailTemplateForm
)

####################
# Admin Management #
####################

def adminlogin(request):
    """
    Handle the admin login.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email)
        errors = {}

        if not email:
            errors['email'] = 'Please Enter Email'

        if not password:
            errors['password'] = 'Please Enter Password'

        if not user.exists():
            errors['user_exists'] = 'Account not found'
        user = authenticate(username=email, password=password)

        if user is None:
            errors['not_admin'] = 'Enter Valid Credentials'
        elif not user.is_superuser and not user.groups.filter(
            name__in=['inventory manager', 'order manager']
        ).exists():
            errors['not_admin'] = 'You do not have permission to access this page.'

        if any(errors.values()):
            return JsonResponse({'errors': errors})

        login(request, user)
        return JsonResponse({'success': True, 'message': 'Login Successfully!'})

    return render(request, 'admin/authentication/login.html')

def logoutadmin(request):
    """
    Handle the admin logout.
    """
    logout(request)
    return redirect('adminlogin')

def dashboard(request):
    """
    Handle the admin dashboard.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    user_count = User.objects.filter(is_superuser=False, is_active=True).count()
    product_count = Product.objects.filter(is_active=True,is_delete=False).count()
    category_count = Category.objects.filter(is_active=True,is_delete=False).count()
    sub_category_count = Category.objects.filter(
    is_active=True,
    is_delete=False,
    parent__isnull=False
    ).count()
    coupon_count = Coupon.objects.filter(is_active=True,is_delete=False).count()
    banner_count = Banner.objects.filter(is_active=True,is_delete=False).count() # pylint: disable=E1101
    contact = ContactUs.objects.all().count()
    order_count = Order.objects.all().count()
    current_year = datetime.now().year
    last_year = current_year - 1
    total_sales = Order.objects.aggregate(total_amount_sum=Sum('total_amount'))
    # Get month-wise sales for the current and last year
    current_year_sales = (
        Order.objects.filter(created_at__year=current_year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('month')
    )

    last_year_sales = (
        Order.objects.filter(created_at__year=last_year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('month')
    )

    # Initialize the dictionary with default values for each month
    monthly_sales_comparison = defaultdict(lambda: {'current_year_sales': 0, 'last_year_sales': 0})

    # Populate the dictionary with current year sales
    for sales in current_year_sales:
        month = sales['month'].month  # Extract the month number from the datetime object
        monthly_sales_comparison[month]['current_year_sales'] = sales['total_sales'] or 0

    # Populate the dictionary with last year sales
    for sales in last_year_sales:
        month = sales['month'].month  # Extract the month number from the datetime object
        monthly_sales_comparison[month]['last_year_sales'] = sales['total_sales'] or 0

    # Prepare lists for chart
    labels = [calendar.month_name[i] for i in range(1, 13)]  # Fixed labels from January to December
    current_year_data = [0] * 12  # Initialize with 0s for each month
    last_year_data = [0] * 12  # Initialize with 0s for each month

    # Fill in the data for each month
    for month, sales in monthly_sales_comparison.items():
        month_index = month - 1  # Get the 0-based index for the month
        current_year_data[month_index] = sales['current_year_sales']
        last_year_data[month_index] = sales['last_year_sales']

    # Calculate percentage change between current month and last month
    def calculate_percentage_change(current, previous):
        if previous == 0:  # Avoid division by zero
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100

    # Get today's date and current month
    today = datetime.now(tz=zoneinfo.ZoneInfo(key='UTC'))
    current_month = today.month

    # Get sales for the current and previous month
    current_month_sales = monthly_sales_comparison[current_month]['current_year_sales']

    if current_month > 1:
        # Previous month is just one month before the current
        previous_month_sales = monthly_sales_comparison[current_month - 1]['current_year_sales']
    else:
        # If current month is January, previous month should be December of the last year
        previous_month_sales = monthly_sales_comparison[12]['last_year_sales']

    # Calculate the percentage change
    percentage_change = calculate_percentage_change(current_month_sales, previous_month_sales)

    # Registrations by date
    registration_data = (
        User.objects.annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Prepare data for the chart
    dates = [data['date'].strftime('%Y-%m-%d') for data in registration_data]  # Format the date
    counts = [data['count'] for data in registration_data]

    # Coupons used per day
    orders_with_coupons = Order.objects.filter(coupon__isnull=False)
    coupon_usage = (
        orders_with_coupons
        .values('created_at__date')  # Group by date
        .annotate(coupon_count=Count('id'))  # Count the number of orders with coupons
        .order_by('created_at__date')
    )

    # Prepare data for chart (labels and data points)
    coupon_labels = [str(entry['created_at__date']) for entry in coupon_usage]
    data_points = [entry['coupon_count'] for entry in coupon_usage]

    context = {
        'product_count':product_count,
        'user_count':user_count,
        "category_count":category_count,
        "sub_category_count":sub_category_count,
        'coupon_count':coupon_count,
        'banner_count':banner_count,
        'contact_count':contact,
        'order_count':order_count,
        'total_sales':total_sales['total_amount_sum'],
        'percentage_change': percentage_change,
        'labels': labels,
        'current_year_data': current_year_data,
        'last_year_data': last_year_data,
        'dates': dates,
        'counts': counts,
        'coupon_labels': coupon_labels,
        'data_points': data_points
    }
    return render(request,'admin/dashboard.html',context)

def export_sales_report_csv(request):
    """Sales Report Csv Generate"""

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
        end_date = datetime.strptime(end_date,'%Y-%m-%d') + timedelta(days=1)
        orders = Order.objects.filter(created_at__range=[start_date,end_date])
    else:
        # Fetch order data (modify this query to fit your Order/OrderItem model structure)
        orders = Order.objects.all()

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['Product Name', 'Total Sold Quantity', 'Current Stock', 'Price', 'Date Range'])

    # Initialize a dictionary to store product data (aggregate by product name)
    product_sales = {}

    # Loop through orders and extract product info
    for order in orders.prefetch_related('order_items__product'):
        for item in order.order_items.all():
        # Assuming `order_items` is the related name for items in Order
            product = item.product

            # If product is already in the dictionary, update the quantity
            if product.name in product_sales:
                product_sales[product.name]['total_sold_quantity'] += item.quantity
            else:
                # If product is not in the dictionary, add it
                product_sales[product.name] = {
                    'total_sold_quantity': item.quantity,
                    'price': product.price,
                    'current_stock': product.quantity
                }

    # Write the aggregated data to the CSV file
    for product_name, data in product_sales.items():
        writer.writerow([product_name, data['total_sold_quantity'],
                        data['current_stock'], data['price'],
        f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}" 
        if start_date and end_date else 'All Time'])

    return response

def customer_registration_report(request):
    """New User Report"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
        original_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date,'%Y-%m-%d') + timedelta(days=1)
        users = User.objects.filter(date_joined__range=[start_date,end_date]).values(
            'email', 'date_joined', 'last_login', 'phone_number'
        )
    else:
        # Fetch all users and their necessary details
        users = User.objects.values('email', 'date_joined', 'last_login', 'phone_number')

    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer_registration_report.csv"'

    # Write to CSV
    writer = csv.writer(response)
    # Header row
    writer.writerow(['Email', 'Join Date', 'Last Login', 'Phone Number','Range Date'])

    # Write each user's data
    for user in users:
        writer.writerow([
            user['email'],  # User email
            user['date_joined'].strftime('%Y-%m-%d %H:%M:%S') if user['date_joined'] else '',
            user['last_login'].strftime('%Y-%m-%d %H:%M:%S') if user['last_login'] else 'Never',
            user['phone_number'] if user['phone_number'] else 'N/A',
            f"{start_date.strftime('%Y-%m-%d')} to {original_end_date.strftime('%Y-%m-%d')}" 
        if start_date and end_date else 'All Time'
        ])

    return response

def coupons_used_report(request):
    """Userd Coupon Report"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
        original_end_date = datetime.strptime(end_date,'%Y-%m-%d')
        end_date = datetime.strptime(end_date,'%Y-%m-%d') + timedelta(days=1)
        # Fetch all orders where coupons were used, ordered by date
        orders_with_coupons = Order.objects.filter(coupon__isnull=False,
        created_at__range=[start_date,end_date]).order_by(
        'created_at').values('user__email', 'coupon__code',
         'coupon__discount_amount', 'created_at', 'total_amount')
    else:
        # Fetch all orders where coupons were used, ordered by date
        orders_with_coupons = Order.objects.filter(coupon__isnull=False).order_by(
        'created_at').values('user__email', 'coupon__code', 
        'coupon__discount_amount', 'created_at', 'total_amount')

    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="coupons_used_report.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write header row
    writer.writerow(['User Email', 'Coupon Code', 'Discount Applied', 'Order Date', 
    'Total Amount','Date Range'])

    # Write data rows
    for order in orders_with_coupons:
        writer.writerow([
            order['user__email'],  # User email
            order['coupon__code'],  # Coupon code
            f"{order['coupon__discount_amount']:.2f}",  # Coupon discount (formatted as decimal)
            order['created_at'].strftime('%Y-%m-%d %H:%M:%S'),  # Order date
            f"{order['total_amount']:.2f}",  # Total order amount (formatted as decimal)
            f"{start_date.strftime('%Y-%m-%d')} to {original_end_date.strftime('%Y-%m-%d')}" 
        if start_date and end_date else 'All Time'
        ])

    return response

###################
# User Management #
###################

@permission_required('users.view_user', raise_exception=True)
def users(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('search','')
    # Filter users to include only active and non-deleted ones
    users = User.objects.filter( # pylint: disable=W0621
        is_active=True,
        is_delete=False,
        is_superuser=False
    ).filter(
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(email__icontains=search_query)
    ).prefetch_related('address').order_by('-id')

    paginator = Paginator(users,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Calculate the start number for the current page
    start_number = (page_obj.number - 1) * paginator.per_page + 1
    context = {
        'page_obj':page_obj,
        'start_number':start_number,
        'search_query':search_query
    }
    if search_query and not users.exists():
        context['not_found_message'] = 'No users found'
    return render(request, 'admin/users/users.html', context)

@permission_required('users.add_user', raise_exception=True)
def add_users(request): # pylint: disable=R0914,R0912,R0915
    """
    Handle the creation.
    """
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    groups = Group.objects.all()
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        groupids = request.POST.getlist('groups[]')

        errors = {}
        if not first_name:
            errors['first_name'] = 'Please Enter First Name'
        # Validate first name format
        elif not re.match(r'^[A-Za-z]+$', first_name):
            errors['first_name'] = 'Please Enter Valid First Name (eg :Faizan)'

        if not last_name:
            errors['last_name'] = 'Please Enter Last Name'
        # Validate last name
        elif not re.match(r'^[A-Za-z]+$',last_name):
            errors['last_name'] = 'Please Enter Valid Last Name (eg :Diwan)'
        # Validate email
        if not email:
            errors['email'] = 'Please Enter Email Address'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Please Enter Valid Email Address'

        # Validate phone number
        if not phone_number:
            errors['phone_number'] = 'Please Enter Phone Number'
        elif not re.match(
            r'^\+?[1-9]\d{1,14}$|^(\(?\d{3}\)?[\s.-]?)?[\s.-]?\d{3}[\s.-]?\d{4}$',
            phone_number
        ):
            errors['phone_number'] = 'Please Enter Valid Phone Number'

        # Validate password
        if not password:
            errors['password'] = 'Please Enter Password'
        elif not re.match(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$',
            password
        ):
            errors['password'] = (
                'Password must be at least 8 characters long and include '
                'at least one uppercase letter, one lowercase letter, one digit, '
                'and one special character.'
            )

        # Password Match
        if not confirm_password:
            errors['confirm_password'] = 'Please Enter Confirm Password'
        elif password != confirm_password:
            errors['confirm_password'] = 'Password and Confirm password does not mactch'

        if not groupids:
            errors['groupids'] = 'Please Select Group'

        # Check User Exitst or not
        if User.objects.filter(email=email).exists():
            errors['email_exists'] = 'Email already Exists Use another one!'

        if any(errors.values()):
            return JsonResponse({'success': False, 'errors': errors})
        try:
            # Create new user without setting password
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )
            # Set the password using set_password method
            new_user.set_password(password)
            new_user.save()

            # Add user to selecetd groups
            for id in groupids: # pylint: disable=W0622
                group = Group.objects.get(id=int(id))
                new_user.groups.add(group)
            mail_context = {
                'first_name':first_name,
                'last_name':last_name,
                'email':email,
                'password':password,
                'phone_number':phone_number
            }
            celery_mail.delay(
                    to_email=email,
                    context=mail_context,
                    template_name='admin-register'
                )
            return JsonResponse({'success': True, 'message': 'User created successfully!'})
        except Exception as e: # pylint: disable=W0718
            return JsonResponse({'success':False,'errors': {'server':str(e)}})
    context = {
    'groups':groups
    }
    return render(request,'admin/users/add_user.html',context)

@permission_required('users.delete_user', raise_exception=True)
def delete_user(request, pk):
    """
    Handle the deletion.
    """
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            messages.error(request, 'User Not Found')
            return redirect('users')
        # Set fields and save
        user.is_active = False
        user.is_delete = True
        user.save()
        messages.success(request, 'User Deleted Successfully!')
        return redirect('users')
    return redirect('users')

@permission_required('users.change_user', raise_exception=True)
def edit_user(request,pk): # pylint: disable=R0914,R0912
    """
    Handle the editing.
    """
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    user = User.objects.get(id=pk)
    groups = Group.objects.all()
    user_groups = user.groups.all()
    user_group_ids = user_groups.values_list('id', flat=True)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        groupids = request.POST.getlist('groups[]')

        errors = {}
        if not first_name:
            errors['first_name'] = 'Please Enter First Name'
        # Validate first name format
        elif not re.match(r'^[A-Za-z]+$', first_name):
            errors['first_name'] = 'Please Enter Valid First Name (eg :Faizan)'

        if not last_name:
            errors['last_name'] = 'Please Enter Last Name'
        # Validate last name
        elif not re.match(r'^[A-Za-z]+$',last_name):
            errors['last_name'] = 'Please Enter Valid Last Name (eg :Diwan)'
        # Validate email
        if not email:
            errors['email'] = 'Please Enter Email Address'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Please Enter Valid Email Address'

        # Validate phone number
        phone_number_pattern = (
            r'^\+?[1-9]\d{1,14}$|'  # International format
            r'^(\(?\d{3}\)?[\s.-]?)?'  # Area code with optional parentheses
            r'[\s.-]?\d{3}'  # Separator and first part of the number
            r'[\s.-]?\d{4}$'  # Separator and last part of the number
        )

        if not phone_number:
            errors['phone_number'] = 'Please Enter Phone Number'
        elif not re.match(phone_number_pattern, phone_number):
            errors['phone_number'] = 'Please Enter valid phone number'

        if any(errors.values()):
            return JsonResponse({'success': False, 'errors': errors})

        try:
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.phone_number=phone_number
            user.save()
            user.groups.clear()
            for id in groupids: # pylint: disable=W0622
                group = Group.objects.get(id=id)
                user.groups.add(group)

            return JsonResponse({'success': True,'message':'User Update Successfully!'})
        except Exception as e: # pylint: disable=W0718
            return JsonResponse({'success':False,'errors':{'server':str(e)}})
    context = {
    'groups':groups,
    'user':user,
    'user_group_ids': user_group_ids
    }
    return render(request,'admin/users/edit_user.html',context)

#####################
# Banner Management #
#####################

@permission_required('customadmin.view_banner',raise_exception=True)
def banner(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    banner = Banner.objects.filter(is_active=True,is_delete=False) # pylint: disable=E1101,W0621
    paginator = Paginator(banner,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1

    context = {
        'page_obj':page_obj,
        'start_number':start_number
    }
    return render(request,'admin/banner/banner.html',context)

@permission_required('customadmin.add_banner', raise_exception=True)
def add_banner(request):
    """
    Handle the creation.
    """
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner added successfully')
            return redirect('banners')
    else:
        form = BannerForm()

    return render(request, 'admin/banner/add_banner.html', {'form': form})

@permission_required('customadmin.delete_banner',raise_exception=True)
def delete_banner(request,pk):
    """
    Handle the deletion.
    """
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        banner = Banner.objects.get(id=pk) # pylint: disable=E1101,W0621
        banner.is_active = False
        banner.is_delete = True
        banner.save()
        messages.success(request,'Banner deleted succssfully')
        return redirect('banners')
    return render(request,'admin/banner/banner.html')

@permission_required('customadmin.change_banner',raise_exception=True)
def edit_banner(request, pk):
    """
    Handle the editing.
    """
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    banner = get_object_or_404(Banner, id=pk) # pylint: disable=W0621
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner updated successfully')
            return redirect('banners')
    else:
        form = BannerForm(instance=banner)

    return render(request, 'admin/banner/edit_banner.html', {'form': form, 'banner': banner})

#########################
# Contact US Management #
#########################

@permission_required('customadmin.view_contact_us',raise_exception=True)
def contact_us(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('search','')
    contact = ContactUs.objects.filter(subject__icontains=search_query)
    paginator = Paginator(contact,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1

    context = {
        'page_obj':page_obj,
        'start_number':start_number,
        'search_query':search_query
    }
    if search_query and not contact.exists():
        context['message_not_found'] = 'Not Contact Us found'
    return render(request,'admin/contact_us/contact_us.html',context)

@permission_required('customadmin.change_contact_us',raise_exception=True)
def contact_us_detail(request, pk):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    contact = get_object_or_404(ContactUs, pk=pk)

    if request.method == 'POST':
        reply = request.POST.get('admin_reply')
        if reply and not contact.is_replied:
            try:
                plain_text_body = strip_tags(reply)
                html_body = reply

                send_contact_email.delay(
                    subject=f"Re: {contact.subject}",
                    plain_text_body=plain_text_body,
                    html_body=html_body,
                    recipient_email=contact.email
                )
                contact.admin_reply = plain_text_body
                contact.is_replied = True
                contact.save()
                messages.success(request,'Mail send successfully')
            except Exception as e: # pylint: disable=W0718
                messages.error(request, 'Something went wrong, please contact the admin.')

            return redirect('contact-us')
    return render(request, 'admin/contact_us/contact_us_detail.html', {'contact': contact})

##################
# CMS Management #
##################

@permission_required('flatpages.view_flat_page',raise_exception=True)
def flatpage_list(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    flatpages = FlatPage.objects.all() # pylint: disable=E1101
    return render(request, 'admin/cms/flatpage.html', {'flatpages': flatpages})

@permission_required('flatpages.add_flat_page',raise_exception=True)
def add_flatpage(request):
    """
    Handle the creation.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        form = CustomFlatPageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Cms Added successfully')
            return redirect('cms')
    else:
        form = CustomFlatPageForm()
    return render(request,'admin/cms/add_flatpage.html',{'form':form})

@permission_required('flatpages.change_flat_page',raise_exception=True)
def edit_flatpage(request,pk):
    """
    Handle the editing.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    flatpage = get_object_or_404(FlatPage, id=pk)
    if request.method == 'POST':
        form = CustomFlatPageForm(request.POST,instance=flatpage)
        if form.is_valid():
            form.save()
            messages.success(request,'Cms updated successfully')
            return redirect('cms')
    else:
        form = CustomFlatPageForm(instance=flatpage)
    return render(request,'admin/cms/edit_flatpage.html',{'form':form,'flatpage':flatpage})

@permission_required('flatpages.delete_flat_page',raise_exception=True)
def delete_flatpage(request,pk):
    """
    Handle the deletion.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    flatpage =  FlatPage.objects.filter(id=pk) # pylint: disable=E1101
    if request.method == 'POST':
        flatpage.delete()
        return redirect('cms')
    return render(request,'admin/cms/flatpage.html')

#############################
# Email Templage Management #
#############################

@permission_required('customadmin.view_email_template',raise_exception=True)
def email_template(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    email_templates = EmailTemplate.objects.filter(is_active=True)
    if not email_templates.exists():
        email_err = 'No email templates available.'
        return render(request, 'admin/email_template/email_template.html', {'email_err': email_err})
    return render(request, 'admin/email_template/email_template.html',
         {'email_templates': email_templates})

@permission_required('customadmin.add_email_template',raise_exception=True)
def add_template(request):
    """
    Handle the creation.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Email Template Created successfully')
            return redirect('emails')
    else:
        form = EmailTemplateForm()
    return render(request,'admin/email_template/add_email_template.html',{'form':form})

@permission_required('customadmin.change_email_template',raise_exception=True)
def edit_email_template(request, pk):
    """
    Handle the editing.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request,'Email template update successfully')
            return redirect('emails')
    else:
        form = EmailTemplateForm(instance=template)
    return render(request, 'admin/email_template/edit_email_template.html', {'form': form})

@permission_required('customadmin.delete_email_template',raise_exception=True)
def delete_email_template(request, pk):
    """
    Handle the deletion.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        template.delete()
        messages.success(request,'Email template delete successfully')
        return redirect('emails')
    return render(request, 'admin/email_template/email_template.html', {'template': template})

##########################
# News Letter Management #
##########################

def news_letter(request):
    """
    Display a list.
    """
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    news_letter_data = NewsletterSubscriber.objects.all()
    search_query = request.GET.get('search','')
    if search_query:
        news_letter_data = NewsletterSubscriber.objects.filter(email__icontains=search_query)
    paginator = Paginator(news_letter_data,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1
    context = {
        'page_obj':page_obj,
        'start_number':start_number,
        'search_query':search_query
    }
    return render(request,'admin/newsletter/news_letter.html',context)
