# pylint: disable=E0401,W1309,C0116,R0914,W0613,W0612
"""
Views for the order application.

This module contains views for listing, creating, editing, and deleting order.
"""
from decimal import Decimal
import json
import requests
import paypalrestsdk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from project.users.models import Address
from project.coupon.models import Coupon
from project.users.models import Wishlist,User
from .models import Product,ProductInOrder,Order

##############
# USER ORDER #
##############

def get_paypal_access_token():
    """
    Get Paypal access token
    """
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, auth=auth, data=data, timeout=50)
    response.raise_for_status()
    return response.json()["access_token"]

def get_cart(request):
    """
    Get Cart
    """
    return request.session.get('cart', {})

def set_cart(request, cart):
    """
    Set Cart
    """
    request.session['cart'] = cart

def cart_detail(request):
    """
    Cart Detail View
    """
    cart = get_cart(request)
    cart_items = []
    cart_sub_total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity
        })
        cart_sub_total += product.price * quantity

    eco_tax = 2
    shipping_cost = 0
    total = cart_sub_total + eco_tax + shipping_cost

    context = {
        'cart_items': cart_items,
        'cart_sub_total': cart_sub_total,
        'eco_tax': eco_tax,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    return render(request, 'front_end/order/cart.html', context)

def add_to_cart(request, pk):
    """
    Add to cart view
    """
    product = get_object_or_404(Product, id=pk)
    cart = get_cart(request)
    current_quantity_in_cart = cart.get(str(pk), 0)

    if current_quantity_in_cart < product.quantity:
        cart[str(pk)] = current_quantity_in_cart + 1
        wishlist_exists = Wishlist.objects.filter(product=product).exists()
        if wishlist_exists:
            Wishlist.objects.filter(product=product).delete()

        set_cart(request, cart)
        response_data = {
            'success': True,
            'message': f"Added {product.name} to your cart.",
            'cart_count': sum(cart.values()),
        }
    else:
        response_data = {
            'success': False,
            'message': f"Sorry, {product.name} is out of stock.",
        }

    return JsonResponse(response_data)

def remove_from_cart(request, pk):
    """
    Remove from cart view
    """
    product = get_object_or_404(Product, id=pk)

    if request.method == 'POST':
        cart = get_cart(request)

        if str(pk) in cart:
            del cart[str(pk)]
            messages.success(request, f"Removed {product.name} from your cart.")

        set_cart(request, cart)

    return redirect('cart-detail')

def update_cart_quantity(request, pk):
    """
    Update cart quantity view
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=pk)
        requested_quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        if requested_quantity > product.quantity: # pylint: disable=R1705
            return JsonResponse({
                'status': 'error',
                'message': f"Sorry, {product.name} is out of stock.",
                'quantity': cart.get(str(pk), 0),
            })
        elif requested_quantity > 0:
            cart[str(pk)] = requested_quantity
            request.session['cart'] = cart
            return JsonResponse({
                'status': 'success',
                'message': 'Cart updated.',
                'quantity': requested_quantity,
                'subtotal': calculate_cart_subtotal(cart),
            })
        else:
            cart.pop(str(pk), None)
            request.session['cart'] = cart
            return JsonResponse({
                'status': 'success',
                'message': 'Product removed from cart.',
                'quantity': 0,
                'subtotal': calculate_cart_subtotal(cart),
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def calculate_cart_subtotal(cart):
    """
    Calcuate cart subtotal function
    """
    subtotal = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal += product.price * quantity
    return subtotal

@login_required
def checkout(request):
    """
    Checkout view
    """
    user = request.user
    cart = get_cart(request)
    cart_items = []
    cart_sub_total = 0
    coupon = None
    discount_amount = Decimal(request.POST.get('discount_amount', 0))

    today = timezone.now().date()
    
    # Fetch active coupons
    active_coupons = Coupon.objects.filter(
        is_delete=False,
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    )

    # Calculate cart subtotal
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity
        })
        cart_sub_total += product.price * quantity
        # Check if the product is out of stock
        if product.quantity < quantity:
            messages.error(request, f"{product.name} is out of stock.")
            return redirect('cart-detail')

    eco_tax = Decimal('2.00')  # Initialize eco_tax
    shipping_cost = Decimal('0.00')  # Initialize shipping_cost
    total = cart_sub_total + eco_tax + shipping_cost - discount_amount
    
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()

        # Handle coupon code input
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                discount_amount = coupon.discount_amount
                messages.success(request, 'Coupon applied.')
                if discount_amount > cart_sub_total:
                    messages.error(request, 'This coupon is not applicable.')
                    discount_amount = 0
            except Coupon.DoesNotExist:
                discount_amount = 0

        # Calculate total amount
        eco_tax = Decimal('2.00')
        shipping_cost = Decimal('0.00')
        total = cart_sub_total + eco_tax + shipping_cost - discount_amount
        
        # Get selected billing and shipping addresses
        billing_address_id = request.POST.get('billing_address')
        shipping_address_id = request.POST.get('shipping_address')

        try:
            billing_address = get_object_or_404(Address, id=billing_address_id, user=user)
            billing_address_str = f"{billing_address.address}, {billing_address.city}, {billing_address.country}, {billing_address.postcode}"
        except:  # Handle case where billing address is not found
            billing_address = None
            messages.error(request, "You need to set a valid billing address before checking out.")
            return redirect('add-address')

        try:
            shipping_address = get_object_or_404(Address, id=shipping_address_id, user=user)
            shipping_address_str = f"{shipping_address.address}, {shipping_address.city}, {shipping_address.country}, {shipping_address.postcode}"
        except:  # Handle case where shipping address is not found
            shipping_address = billing_address  # Fallback to billing address
            shipping_address_str = f"{shipping_address.address}, {shipping_address.city}, {shipping_address.country}, {shipping_address.postcode}"


        payment_method = request.POST.get('payment_method')
        shipping_method = int(request.POST.get('shipping_method', 1))

        if payment_method:
            if payment_method == 'paypal':
                # Payment processing with PayPal
                request.session['order_data'] = {
                    'user_id': user.id,
                    'total_amount': str(total),
                    'billing_address': billing_address_str,
                    'shipping_address': shipping_address_str,
                    'shipping_method': shipping_method,
                    'coupon_id': coupon.id if coupon else None,
                    'discount_amount': str(discount_amount)
                }
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri('/payment/paypal/execute/'),
                        "cancel_url": request.build_absolute_uri('/payment/paypal/cancel/')
                    },
                    "transactions": [{
                        "item_list": {
                            "items": [{
                                "name": "Order",
                                "sku": "item",
                                "price": f"{total:.2f}",
                                "currency": "USD",
                                "quantity": 1
                            }]
                        },
                        "amount": {
                            "total": f"{total:.2f}",
                            "currency": "USD"
                        },
                        "description": "This is the payment transaction description."
                    }]
                })
                if payment.create():
                    for link in payment.links:
                        if link.rel == "approval_url":
                            return redirect(link.href)
                else:
                    messages.error(request, "An error occurred while processing your payment")

            elif payment_method == 'cash_on_delivery':
                # Create order for cash on delivery
                order = Order.objects.create(
                    user=user,
                    total_amount=total,
                    payment_status=3,
                    billing_address=billing_address_str,
                    shipping_address=shipping_address_str,
                    shipping_method=shipping_method,
                    coupon=coupon,
                    discount_amount=discount_amount,
                    payment_method=2
                )

                # Save each product in the order
                for item in cart_items:
                    product = item['product']
                    product.quantity -= item['quantity']  # Deduct quantity
                    product.save()
                    ProductInOrder.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=product.price
                    )
                messages.success(request, "Order placed successfully with Cash on Delivery!")
                request.session['cart'] = {}
                return redirect('order-confirmation', pk=order.id)

    # For GET request, get the user's addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_items': cart_items,
        'cart_sub_total': cart_sub_total,
        'eco_tax': Decimal('2.00'),
        'shipping_cost': Decimal('0.00'),
        'total': total,
        'billing_address': billing_address if 'billing_address' in locals() else None,
        'shipping_address': shipping_address if 'shipping_address' in locals() else None,
        'coupons': active_coupons,
        'applied_coupon': coupon,
        'discount_amount': discount_amount,
        'addresses': addresses  # Pass the user's addresses to the template
    }

    return render(request, 'front_end/order/checkout.html', context)

@login_required
def paypal_execute_payment(request): #pylint: disable=R0914
    """
    Paypal execute view
    """
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if payment_id and payer_id:
        access_token = get_paypal_access_token()
        url = f"https://api.sandbox.paypal.com/v1/payments/payment/{payment_id}/execute"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        data = {
            "payer_id": payer_id
        }
        response = requests.post(url, headers=headers, json=data, timeout=50)

        if response.status_code == 200:
            # Payment executed successfully
            order_data = request.session.get('order_data')
            if order_data: # pylint: disable=R1705
                user = request.user
                coupon = Coupon.objects.get(
                id=order_data['coupon_id']) if order_data['coupon_id'] else None
                discount_amount = Decimal(order_data['discount_amount'])
                total_amount = Decimal(order_data['total_amount'])
                billing_address= order_data['billing_address']
                shipping_address= order_data['shipping_address']
                shipping_method = order_data['shipping_method']

                order = Order.objects.create( #pylint: disable=E1101
                    user=user,
                    total_amount=total_amount,
                    billing_address=billing_address,
                    shipping_address=shipping_address,
                    shipping_method=shipping_method,
                    coupon=coupon,
                    discount_amount=discount_amount,
                    paypal_payment_id=payment_id,
                    payment_method=1
                )
                cart = get_cart(request)
                for product_id, quantity in cart.items():
                    product = Product.objects.get(id=product_id)
                    product.quantity = product.quantity - quantity
                    product.save()
                    ProductInOrder.objects.create( #pylint: disable=E1101
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price * quantity
                    )
                messages.success(request, "Payment completed successfully!")
                return redirect('order-confirmation', pk=order.id)
            else:
                messages.error(request, "Please try again.")
                return redirect('checkout')
        else:
            # Payment execution failed
            messages.error(request, "Payment execution failed. Please try again.")
            return redirect('checkout')
    else:
        messages.error(request, "Payment ID or Payer ID missing.")
        return redirect('checkout')

@csrf_exempt
def paypal_webhook(request):
    """
    PayPal Webhook listener view
    """
    if request.method == 'POST':
        webhook_event = json.loads(request.body)
        print('webhook_event: ', webhook_event)

        # Verify the webhook event type
        event_type = webhook_event.get('event_type')
        print('event_type: ', event_type)

        if event_type == 'PAYMENT.SALE.COMPLETED':
            # Payment has been completed
            payment_id = webhook_event['resource']['parent_payment']

            # Update the order in system
            try:
                order = Order.objects.get(paypal_payment_id=payment_id)
                order.payment_status = 1
                order.save()
                request.session['cart'] = {}
                # send_order_confirmation_email(order)

                return HttpResponse(status=200)

            except Order.DoesNotExist:
                # Handle case where order does not exist
                return HttpResponse(status=404)

        elif event_type == 'PAYMENT.SALE.DENIED':
            # Handle denied payment scenario
            payment_id = webhook_event['resource']['parent_payment']
            try:
                order = Order.objects.get(paypal_payment_id=payment_id)
                order.payment_status = 2  # Mark as Denied
                order.save()
                return HttpResponse(status=200)
            except Order.DoesNotExist:
                return HttpResponse(status=404)

        # Add more webhook event types as needed

    return HttpResponse(status=400)

@login_required
def paypal_cancel_payment(request):
    """
    Paypal cancel view
    """
    messages.warning(request, "Payment cancelled by the user.")
    return redirect('checkout')

@login_required
def order_confirmation(request,pk):
    """
    Order confirmation view
    """
    # Fetch the order based on the provided order ID
    order = get_object_or_404(Order, id=pk, user=request.user)

    # Render the order confirmation page
    return render(request, 'front_end/order/order_confirmation.html',{'order':order})

def track_order(request):
    order_status = None
    order_not_found = False
    order_id = request.POST.get('order_id') if request.method == 'POST' else ''
    email = request.POST.get('email') if request.method == 'POST' else ''

    if order_id:
        try:
            user = User.objects.get(email=email)
            order = Order.objects.get(order_id=order_id,user=user)
            order_status = order.status  # This is the integer status
        except User.DoesNotExist:
            order_not_found = True
        except Order.DoesNotExist:
            order_not_found = True

    return render(request, 'front_end/order/user/track_order.html', {
        'order_id': order_id,
        'email':email,
        'order_status': order_status,
        'order': order if order_status else None,
        'order_not_found': order_not_found,
    })

@login_required
def order_list(request):
    """
    Order list view
    """
    query = request.GET.get('q', '')
    orders = Order.objects.filter(user=request.user).order_by('-datetime_of_payment') #pylint: disable=E1101
    if query:
        print('query: ', query)
        # If there is a search query, filter by order fields (e.g., order ID, product name)
        orders = orders.filter(
            Q(order_id__icontains=query)
        ).distinct()
    paginator = Paginator(orders,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': query,
    }
    return render(request, 'front_end/order/user/order_list.html', context)

@login_required
def order_detail_user(request, pk):
    """
    Order detail view for user
    """
    order = get_object_or_404(Order, id=pk,user=request.user)

    order_items = [
        {
            'product': item.product,
            'quantity': item.quantity,
            'price': item.price,
            'total_price': item.quantity * item.price,
        }
        for item in order.order_items.all()
    ]

    context = {
        'order': order,
        'order_items': order_items,
        'estimated_delivery_date': order.estimated_delivery_date
    }

    return render(request, 'front_end/order/user/order_detail_user.html', context)

@login_required
def generate_invoice_pdf(request, order_id):
    """
    generate_invoice_pdf view for user
    """
    try:
        # Fetch the order details
        order = Order.objects.get(id=order_id)
        items = order.order_items.all()  # Fetch related order items

        # Create a HttpResponse object with PDF content type
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_id}.pdf"'

        # Create a PDF canvas using reportlab
        p = canvas.Canvas(response, pagesize=A4)

        # Start writing to the PDF
        width, height = A4
        p.setFont("Helvetica", 12)

        # Invoice title
        p.drawString(200, height - 50, f"Invoice #{order.id}")
        p.drawString(50, height - 80, f"Customer: {order.user.email}")
        p.drawString(50, height - 100, f"Billing Address: {order.billing_address}")
        p.drawString(50, height - 120, f"Shipping Address: {order.shipping_address}")

        # Mapping payment status
        payment_status_dict = dict(order.payment_status_choice)
        payment_status = payment_status_dict.get(order.payment_status, "Unknown")

        # Add Payment Type to PDF
        p.drawString(50, height - 140, f"Payment Type: {payment_status}")

        # Applied Discount near Payment Status
        applied_discount_str = f"Applied Discount: -${order.discount_amount:.2f}"
        p.drawString(50, height - 160, applied_discount_str)

        # Set column widths
        col_widths = {
            'product': 200,
            'quantity': 50,
            'unit_price': 100,
            'total_price': 100,
        }

        # Draw table header
        header_y = height - 170
        p.setFillColor(colors.grey)
        p.rect(50, header_y - 20, sum(col_widths.values()), 20, fill=1)
        p.setFillColor(colors.black)
        p.drawString(50, header_y - 15, "Product")
        p.drawString(50 + col_widths['product'], header_y - 15, "Quantity")
        p.drawString(50 + col_widths['product'] + col_widths['quantity'],
                     header_y - 15, "Unit Price")
        p.drawString(50 + col_widths['product'] + col_widths['quantity']
                     + col_widths['unit_price'], header_y - 15, "Total Price")

        # Draw header line
        p.line(50, header_y - 20, 50 + sum(col_widths.values()), header_y - 20)

        # Loop through order items and add to the PDF
        y_position = header_y - 40
        p.setFont("Helvetica", 12)

        for item in items:
            # Draw product name with wrapping
            product_name = item.product.name
            product_lines = []
            max_line_length = col_widths['product'] // 8

            # Wrap the product name based on calculated length
            while product_name:
                product_lines.append(product_name[:max_line_length])
                product_name = product_name[max_line_length:]

            # Draw each line of the product name
            for line in product_lines:
                p.drawString(50, y_position, line)
                y_position -= 15  # Move down for the next line

            # Draw quantity
            p.drawString(50 + col_widths['product'], y_position + 15, str(item.quantity))

            # Draw unit price
            p.drawString(50 + col_widths['product'] + col_widths['quantity'],
                         y_position + 15, f"${item.price:.2f}")

            # Calculate and draw total price
            total_price = item.price * item.quantity
            p.drawString(50 + col_widths['product'] +
            col_widths['quantity'] + col_widths['unit_price'],
            y_position + 15, f"${total_price:.2f}")

            # Draw item row bottom line
            p.line(50, y_position + 10, 50 + sum(col_widths.values()), y_position + 10)
            y_position -= 20  # Move down for the next row

        # Total Amount
        y_position -= 10  # Extra space before the total
        total_amount_str = f"Total Amount: ${order.total_amount:.2f}"
        p.drawString(350, y_position, total_amount_str)

        # Draw a complete line under the total amount
        line_y_position = y_position - 5
        p.line(50, line_y_position, 50 + sum(col_widths.values()), line_y_position)

        # Close the PDF object
        p.showPage()
        p.save()

        # Return the PDF response
        return response
    except Order.DoesNotExist:
        return HttpResponse('Order not found', status=404)

@login_required
def invoice_view(request, order_id):
    """
    invoice_pdf view for user
    """
    # Retrieve the order object or return a 404 if not found
    order = get_object_or_404(Order, id=order_id)
    items = order.order_items.all()

    # Map payment status to a readable format
    payment_status_dict = dict(order.payment_status_choice)
    payment_status = payment_status_dict.get(order.payment_status, "Unknown")

    # Prepare the context for the template
    context = {
        'order': order,
        'items': items,
        'payment_status': payment_status,
    }

    # Render the invoice template and return the HTTP response
    return render(request, 'front_end/invoice.html', context)
