from django.shortcuts import render, redirect,get_object_or_404
from .models import Product
from django.http import JsonResponse

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

    # Calculate totals
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
    return render(request, 'front_end/cart/cart.html', context)

def add_to_cart(request, pk):
    product = Product.objects.get(id=pk)
    cart = get_cart(request)
    
    # Update cart quantity
    if str(pk) in cart:
        cart[str(pk)] += 1
    else:
        cart[str(pk)] = 1

    set_cart(request, cart)
    return redirect('cart-detail')

def remove_from_cart(request, pk):
    if request.method == 'POST':
        cart = get_cart(request)
        
        if str(pk) in cart:
            del cart[str(pk)]
        
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
                'subtotal': calculate_cart_subtotal(cart),  # Add a helper function to calculate subtotal
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
