# pylint: disable=E0401
"""
Views for the CustomAdmin application.

This module contains views for listing, creating, editing, and deleting CustomAdmin.
"""
from datetime import datetime, timedelta
from django.shortcuts import redirect,render,get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.contrib import messages

from project.customadmin.tasks import celery_mail
from project.utils.custom_required import admin_required
from project.users.models import Address
from .models import Order,ProductInOrder
from .forms import OrderStatusForm

####################
# Order Management #
####################

@admin_required
@permission_required('product.view_order',raise_exception=True)
def order(request):
    """
    Display a list of orders with filters.
    """
    # Get search and filter parameters from the GET request
    search_query = request.GET.get('search', '')
    payment_status = request.GET.get('payment_status', '')
    order_status = request.GET.get('order_status', '')
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    # Start with all orders
    orders = Order.objects.all()

    # Apply filters progressively
    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    if order_status:
        orders = orders.filter(status=order_status)

    if start_date and end_date:
        try:
            # Convert string to datetime
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            end_date = end_date + timedelta(days=1)
            # Filter orders based on date range
            orders = orders.filter(created_at__range=[start_date, end_date])
        except ValueError:
            print('Error in date filter: invalid date format')

    # Apply search query filter (order_id)
    if search_query:
        orders = orders.filter(order_id__icontains=search_query)

    # Order by latest first
    orders = orders.order_by('-id')  # pylint: disable=E1101

    # Apply pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1

    # After conversion to datetime, you can use strftime
    start_date_str = start_date.strftime("%Y-%m-%d") if isinstance(start_date, datetime) else ''
    end_date_str = end_date.strftime("%Y-%m-%d") if isinstance(end_date, datetime) else ''

    # Prepare context for the template
    context = {
        'page_obj': page_obj,
        'start_number': start_number,
        'search_query': search_query,
        'payment_status': payment_status,
        'order_status': order_status,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }

    # Add a message if no orders are found
    if search_query and not orders.exists():
        context['message_not_found'] = 'No orders found'

    return render(request, 'admin/orders/orders.html', context)

@admin_required
@permission_required('product.change_order',raise_exception=True)
def order_detail(request, pk):
    """
    Display a list.
    """
    # Fetch the order details
    order = get_object_or_404(Order, id=pk) # pylint: disable=W0621
    products_in_order = ProductInOrder.objects.filter(order=order) # pylint: disable=E1101
    customer_address = Address.objects.filter(user=order.user, is_active=True).first()

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            order_data = {
                'order_id': order.order_id,
                'datetime_of_payment': 
                order.datetime_of_payment.isoformat()
                if order.datetime_of_payment else None,
                'shipping_method': order.get_shipping_method_display(),
                'payment_status': order.get_payment_status_display(),
                'total_amount': order.total_amount,
                'first_name': order.user.first_name,
                'order_status': dict(Order.status_choice).get(new_status, 'Unknown'),
                'is_cash_on_delivery': order.is_cash_on_delivery,
            }
            products_data = [
                {
                    'product_name': product_in_order.product.name,
                    'quantity': product_in_order.quantity,
                    'price': product_in_order.price,
                }
                for product_in_order in products_in_order
            ]
            customer_address_data = {
                'address': customer_address.address,
                'city': customer_address.city,
                'country': customer_address.country,
                'district': customer_address.district,
                'postcode': customer_address.postcode,
            } if customer_address else None
            context_email = {
                'order_id': order_data['order_id'],
                'datetime_of_payment': order_data['datetime_of_payment'],
                'shipping_method': order_data['shipping_method'],
                'payment_status': order_data['payment_status'],
                'total_amount': order_data['total_amount'],
                'first_name': order_data['first_name'],
                'order_status': order_data['order_status'],
                'products': products_data,
                'customer_address': customer_address_data,
                'is_cash_on_delivery': order_data['is_cash_on_delivery']
            }
            try:
                celery_mail.delay(
                    to_email=order.user.email,
                    context=context_email,
                    template_name='order_status'
                )
            except Exception as e: # pylint: disable=W0718
                print('Error sending email:', e)
            form.save()
            messages.success(request, 'Order status updated successfully.')
            return redirect('order-detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)

    context = {
        'order': order,
        'products_in_order': products_in_order,
        'customer_address': customer_address,
        'form': form
    }

    return render(request, 'admin/orders/order_detail.html', context)
