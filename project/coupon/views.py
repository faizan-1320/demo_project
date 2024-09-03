from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Coupon
from .forms import CouponForm
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required
from project.utils import custom_required

# Create your views here.
@permission_required('coupon.view_coupon',raise_exception=True)
def coupon(request):
    if not custom_required.check_login_admin(request.user):
        return redirect('admin-custom')
    try:
        today = timezone.now().date()
        search_query = request.GET.get('search','')
        coupons = Coupon.objects.filter(is_delete=False,code__icontains=search_query)
        for coupon in coupons:
            if coupon.is_active and coupon.start_date <= today <= coupon.end_date:
                coupon.currently_active = True
            else:
                coupon.currently_active = False
        paginator = Paginator(coupons,10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        start_number = (page_obj.number - 1) * paginator.per_page + 1
        context = {
            'page_obj':page_obj,
            'start_number':start_number,
            'search_query':search_query
        }
        if search_query and not coupons.exists():
            context['not_found_message'] = 'No Coupon found'
    except Coupon.DoesNotExist:
        coupon_err = 'No data available'
        return render(request, 'admin/coupon/coupon.html', {'coupon_err': coupon_err})
    return render(request, 'admin/coupon/coupon.html', context)

@permission_required('coupon.add_coupon',raise_exception=True)
def add_coupon(request):
    if not custom_required.check_login_admin(request.user):
        return redirect('admin-custom')
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('coupons')
        else:
            errors = form.errors.as_json()
    else:
        form = CouponForm()
    return render(request, 'admin/coupon/add_coupon.html', {'form': form, 'errors': errors})

@permission_required('coupon.change_coupon',raise_exception=True)
def edit_coupon(request, pk):
    if not custom_required.check_login_admin(request.user):
        return redirect('admin-custom')
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully!')
            return redirect('coupons')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'admin/coupon/edit_coupon.html', {'form': form})

@permission_required('coupon.delete_coupon',raise_exception=True)
def delete_coupon(request, pk):
    if not custom_required.check_login_admin(request.user):
        return redirect('admin-custom')
    if request.method == 'POST':
        coupon = get_object_or_404(Coupon, id=pk)
        coupon.is_delete = True
        coupon.save()
        messages.success(request, 'Coupon deleted successfully!')
        return redirect('coupons')
    return render(request, 'admin/coupon/coupon.html', {'coupon': coupon})
