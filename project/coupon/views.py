from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Coupon
from .forms import CouponForm
from django.core.paginator import Paginator

# Create your views here.
def coupon(request):
    try:
        coupons = Coupon.objects.filter(is_delete=False)
        paginator = Paginator(coupons,10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        start_number = (page_obj.number - 1) * paginator.per_page + 1
        context = {
            'page_obj':page_obj,
            'start_number':start_number
        }
        if not coupons:
            raise Coupon.DoesNotExist
    except Coupon.DoesNotExist:
        coupon_err = 'No data available'
        return render(request, 'admin/coupon/coupon.html', {'coupon_err': coupon_err})
    return render(request, 'admin/coupon/coupon.html', context)

def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('coupon')
    else:
        form = CouponForm()
    return render(request, 'admin/coupon/add_coupon.html', {'form': form})

def edit_coupon(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully!')
            return redirect('coupon')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'admin/coupon/edit_coupon.html', {'form': form})

def delete_coupon(request, pk):
    if request.method == 'POST':
        coupon = get_object_or_404(Coupon, id=pk)
        coupon.is_delete = True
        coupon.save()
        messages.success(request, 'Coupon deleted successfully!')
        return redirect('coupon')
    return render(request, 'admin/coupon/coupon.html', {'coupon': coupon})