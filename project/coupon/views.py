"""
Views for the Coupon application.

This module contains views for listing, creating, editing, and deleting coupons.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required
from django.db.models import Case, Value, When
from project.utils.custom_required import admin_required # pylint: disable=E0401
from .models import Coupon
from .forms import CouponForm

# View for listing coupons with pagination and search functionality
@admin_required
@permission_required('coupon.view_coupon', raise_exception=True)
def coupon_list(request):
    """
    Display a list of coupons with pagination and search functionality.
    """
    today = timezone.now().date()
    search_query = request.GET.get('search', '')
    # coupons = Coupon.objects.filter(is_delete=False, code__icontains=search_query)
    coupons = Coupon.objects.filter(
    is_delete=False,
    code__icontains=search_query
    ).annotate(
    is_coupon_active=Case(
        When(start_date__lte=today, end_date__gte=today, then=Value(True)))
    ).order_by('-is_coupon_active', '-start_date')

    for coupon in coupons:
        coupon.currently_active = coupon.is_active and coupon.start_date <= today <= coupon.end_date

    paginator = Paginator(coupons, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_number = (page_obj.number - 1) * paginator.per_page + 1

    context = {
        'page_obj': page_obj,
        'start_number': start_number,
        'search_query': search_query,
    }

    if search_query and not coupons.exists():
        context['not_found_message'] = 'No Coupon found'

    return render(request, 'admin/coupon/coupon.html', context)

# View for adding a new coupon
@admin_required
@permission_required('coupon.add_coupon', raise_exception=True)
def add_coupon(request):
    """
    Handle the creation of a new coupon.
    """
    errors = None
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('coupons')
        errors = form.errors
    form = CouponForm()

    return render(request, 'admin/coupon/add_coupon.html', {'form': form, 'errors': errors})

# View for editing an existing coupon
@admin_required
@permission_required('coupon.change_coupon', raise_exception=True)
def edit_coupon(request, pk):
    """
    Handle the editing of an existing coupon.
    """
    coupon_instance = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully!')
            return redirect('coupons')
    else:
        form = CouponForm(instance=coupon_instance)

    return render(request, 'admin/coupon/edit_coupon.html', {'form': form})

# View for deleting a coupon
@admin_required
@permission_required('coupon.delete_coupon', raise_exception=True)
def delete_coupon(request, pk):
    """
    Handle the deletion of a coupon by marking it as deleted.
    """
    if request.method == 'POST':
        coupon_instance = get_object_or_404(Coupon, id=pk)
        coupon_instance.is_delete = True
        coupon_instance.save()
        messages.success(request, 'Coupon deleted successfully!')
        return redirect('coupons')

    return render(request, 'admin/coupon/coupon.html', {'coupon': coupon_instance})
