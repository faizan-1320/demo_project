from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,ProductAttributeValue
from collections import defaultdict
from .models import Product, Review, Rating
from .forms import ReviewForm, RatingForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def product_detail(request,pk):
    product = get_object_or_404(Product.objects.prefetch_related('product'), id=pk)
    attributes = ProductAttributeValue.objects.filter(product=product)
    reviews = Review.objects.filter(product=product, is_active=True, is_delete=False)
    ratings = Rating.objects.filter(product=product, is_active=True, is_delete=False)
    # Calculate average rating
    # average_rating = ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
    grouped_attributes = defaultdict(list)
    for attribute in attributes:
        grouped_attributes[attribute.product_attribute.name].append(attribute.value)
    grouped_attributes = dict(grouped_attributes)

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
            context = {
        'product': product,
        'images': product.product.all(),
        'grouped_attributes': grouped_attributes,
        'review_form': review_form,
        'rating_form': rating_form,
        'ratings': ratings,
        # 'average_rating': average_rating,
    }

            return render(request,'front_end/product/product_detail.html',context)  # Adjust redirect as needed

    context = {
        'product': product,
        'images': product.product.all(),
        'grouped_attributes': grouped_attributes,
        'review_form': review_form,
        'rating_form': rating_form,
        'ratings': ratings,
        # 'average_rating': average_rating,
    }
    return render(request,'front_end/product/product_detail.html',context)

@login_required
def product_review_and_rating(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    return render(request, 'product/review_and_rating.html')