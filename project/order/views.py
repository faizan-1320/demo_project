import paypalrestsdk
import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product,ProductInOrder,Order
from project.users.models import Address
from project.coupon.models import Coupon
from decimal import Decimal

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": 'AQIomGzeKsnNgkKyf9kfWu27UOllP_MoMpEbeUH0qVEK3VLhQZr9rBj8Icn4CMsxf8AEQco6N0w7wdKt',
    "client_secret": 'EE6UMMHCzd5A_KXEb695XjLLVb-Uf_-1Zhy3fKM9PIh5dkZPS8e1pr99UHFTyMe56hhqa24kZUj3xq2r',
    "log_level": "DEBUG"
})

def get_paypal_access_token():
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"  # Use "https://api.paypal.com/v1/oauth2/token" for live
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, auth=auth, data=data)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json()["access_token"]

def get_cart(request):
    return request.session.get('cart', {})

def set_cart(request, cart):
    request.session['cart'] = cart

def cart_detail(request):
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
    product = get_object_or_404(Product, id=pk)
    cart = get_cart(request)
    
    if str(pk) in cart:
        cart[str(pk)] += 1
        messages.success(request, f"Added another {product.name} to your cart.")
    else:
        cart[str(pk)] = 1
        messages.success(request, f"Added {product.name} to your cart.")
    
    set_cart(request, cart)
    return redirect('home')

def remove_from_cart(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    if request.method == 'POST':
        cart = get_cart(request)
        
        if str(pk) in cart:
            del cart[str(pk)]
            messages.success(request, f"Removed {product.name} from your cart.")
        
        set_cart(request, cart)
    
    return redirect('cart-detail')

def update_cart_quantity(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=pk)
        requested_quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        if requested_quantity > product.quantity:
            return JsonResponse({
                'status': 'error',
                'message': 'Not enough stock available.',
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
    subtotal = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal += product.price * quantity
    return subtotal

@login_required
def checkout(request):
    user = request.user
    cart = get_cart(request)
    cart_items = []
    cart_sub_total = 0
    coupon = None
    coupon_code = request.POST.get('coupon_code')
    discount_amount = Decimal(request.POST.get('discount_amount', 0))

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity
        })
        cart_sub_total += product.price * quantity

    if request.method == 'POST':
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

        eco_tax = 2
        shipping_cost = 0
        total = cart_sub_total + eco_tax + shipping_cost - discount_amount
        try:
            primary_address = get_object_or_404(Address, user=user, is_primary=True)
        except:
            primary_address = None
            messages.error(request, "You need to set a primary address before checking out.")
            return redirect('add-address')

        payment_method = request.POST.get('payment_method')
        shipping_method = int(request.POST.get('shipping_method', 1))

        if payment_method:
            print('coupon: ', coupon)
            print('discount_amount: ', discount_amount)

            if payment_method == 'paypal':
                request.session['order_data'] = {
                'user_id': user.id,
                'total_amount': str(total),
                'address_id': primary_address.id,
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
                                "price": "{:.2f}".format(total),
                                "currency": "USD",
                                "quantity": 1
                            }]
                        },
                        "amount": {
                            "total": "{:.2f}".format(total),
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
                    messages.error(request, f"An error occurred while processing your payment: {payment.error}")

            elif payment_method == 'cash_on_delivery':
                order = Order.objects.create(
                user=user,
                total_amount=total,
                payment_status=3,
                address=primary_address,
                shipping_method=shipping_method,
                coupon=coupon,
                discount_amount=discount_amount,
                )
            
                # Save each product in the order
                for item in cart_items:
                    product = item['product']
                    product = Product.objects.get(id=product.id)
                    product.quantity = product.quantity - item['quantity']
                    product.save()
                    ProductInOrder.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=item['total_price']
                    )
                messages.success(request, "Order placed successfully with Cash on Delivery!")
                request.session['cart'] = {}
                order.payment_status = 6  # Set payment status to CASH_ON_DELIVERY
                order.save()
                return redirect('order-confirmation', pk=order.id)
    else:
        eco_tax = Decimal('2.00')
        shipping_cost = Decimal('0.00')
        total = cart_sub_total + eco_tax + shipping_cost - discount_amount
        try:
            primary_address = get_object_or_404(Address, user=user, is_primary=True)
        except:
            primary_address = None
            messages.error(request, "You need to set a primary address before checking out.")
            return redirect('add-address')  

    context = {
        'cart_items': cart_items,
        'cart_sub_total': cart_sub_total,
        'eco_tax': eco_tax,
        'shipping_cost': shipping_cost,
        'total': total,
        'primary_address': primary_address,
        'coupons': Coupon.objects.all(),
        'applied_coupon': coupon,
        'discount_amount': discount_amount
    }
    
    return render(request, 'front_end/order/checkout.html', context)

@login_required
def paypal_execute_payment(request):
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
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            # Payment executed successfully
            payment = response.json()
            order_data = request.session.get('order_data')
            if order_data:
                user = request.user
                address = Address.objects.get(id=order_data['address_id'])
                coupon = Coupon.objects.get(id=order_data['coupon_id']) if order_data['coupon_id'] else None
                discount_amount = Decimal(order_data['discount_amount'])
                total_amount = Decimal(order_data['total_amount'])
                shipping_method = order_data['shipping_method']

                order = Order.objects.create(
                    user=user,
                    total_amount=total_amount,
                    payment_status=1,
                    address=address,
                    shipping_method=shipping_method,
                    coupon=coupon,
                    discount_amount=discount_amount,
                )
                cart = get_cart(request)
                for product_id, quantity in cart.items():
                    product = Product.objects.get(id=product_id)
                    product.quantity = product.quantity - quantity
                    product.save()
                    ProductInOrder.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price * quantity
                    )
                request.session['cart'] = {}
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

@login_required
def paypal_cancel_payment(request):
    messages.warning(request, "Payment cancelled by the user.")
    return redirect('checkout')

@login_required
def order_confirmation(request,pk):
    # Fetch the order based on the provided order ID
    order = get_object_or_404(Order, id=pk, user=request.user)
    
    # Render the order confirmation page
    return render(request, 'front_end/order/order_confirmation.html',{'order':order})

##############
# USER ORDER #
##############

@login_required
def order_list(request):
    # Retrieve orders for the logged-in user
    orders = Order.objects.filter(user=request.user).order_by('-datetime_of_payment')

    context = {
        'orders': orders,
    }
    return render(request, 'front_end/order/user/order_list.html', context)

@login_required
def order_detail(request, pk):
    # Retrieve the specific order by its primary key (pk)
    order = get_object_or_404(Order, id=pk)

    # Calculate total price for each order item
    order_items = [
        {
            'product': item.product,
            'quantity': item.quantity,
            'price': item.price,
            'total_price': item.quantity * item.price
        }
        for item in order.productinorder_set.all()
    ]

    # Context to pass to the template
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'front_end/order/user/order_detail_user.html', context)