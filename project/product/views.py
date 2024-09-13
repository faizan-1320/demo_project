"""
Views for the product application.

This module contains views for listing, creating, editing, and deleting product.
"""
from collections import defaultdict
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from .models import Product,ProductAttributeValue,Review, Rating
from .forms import ReviewForm, RatingForm

# Create your views here.
def product_detail(request,pk):
    """
    Product Listing View
    """
    product = get_object_or_404(Product.objects.prefetch_related('product'), id=pk) # pylint: disable=E1101
    attributes = ProductAttributeValue.objects.filter(product=product) # pylint: disable=E1101
    reviews = Review.objects.filter(product=product, is_active=True, is_delete=False) # pylint: disable=E1101
    ratings = Rating.objects.filter(product=product, is_active=True, is_delete=False) # pylint: disable=E1101

    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    grouped_attributes = defaultdict(list)
    for attribute in attributes:
        grouped_attributes[attribute.product_attribute.name].append(attribute.value)
    grouped_attributes = dict(grouped_attributes)

    reviews_with_ratings = []
    for review in reviews:
        rating = ratings.filter(user=review.user, product=review.product).first()
        reviews_with_ratings.append({
            'review': review,
            'rating': rating.rating if rating else None
        })

    context = {
        'product': product,
        'images': product.product.all(),
        'attributes':attributes,
        'grouped_attributes': grouped_attributes,
        'ratings': reviews_with_ratings,
        'reviews': reviews,
        'average_rating':average_rating
    }
    return render(request,'front_end/product/product_detail.html',context)

@login_required
def product_review_and_rating(request, product_id):
    """
    Product Detail Listing View
    """
    product = get_object_or_404(Product, id=product_id)
    review_form = ReviewForm(request.POST or None)
    rating_form = RatingForm(request.POST or None)

    if request.method == 'POST':
        if review_form.is_valid() and rating_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()

            rating = rating_form.save(commit=False)
            rating.user = request.user
            rating.product = product
            rating.save()

            return redirect('product-detail', product.id)

    context = {
        'product': product,
        'review_form': review_form,
        'rating_form': rating_form,
    }
    return render(request, 'front_end/product/review_and_rating.html', context)
