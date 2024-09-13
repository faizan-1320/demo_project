"""
Views for the CustomAdmin application.

This module contains views for listing, creating, editing, and deleting CustomAdmin.
"""
from django.shortcuts import redirect,render,get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.contrib import messages

from project.customadmin.tasks import celery_mail # pylint: disable=E0401
from project.utils import custom_required # pylint: disable=E0401
from project.users.models import Address # pylint: disable=E0401
from .models import Order,ProductInOrder
from .forms import OrderStatusForm

####################
# Order Management #
####################

@permission_required('product.view_order',raise_exception=True)
def order(request):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')
    search_query = request.GET.get('search','')
    orders = Order.objects.filter(order_id__icontains=search_query) # pylint: disable=E1101
    paginator = Paginator(orders,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1

    context = {
        'page_obj':page_obj,
        'start_number':start_number,
        'search_query':search_query
    }
    if search_query and not orders.exists():
        context['message_not_found'] = 'Not order found'
    return render(request, 'admin/orders/orders.html', context)

@permission_required('product.change_order',raise_exception=True)
def order_detail(request, pk):
    """
    Display a list.
    """
    # Check if the user is an admin
    if not custom_required.check_login_admin(request.user):
        return redirect('adminlogin')

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
                'shipping_method': order.shipping_method,
                'payment_status': order.payment_status,
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
