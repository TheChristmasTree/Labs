# Create your views here.

from .models import Shop, Dish, Orders
from customer.models import Customer
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from .models import Comments


def show_dish(request):
    template_name = 'dish/dish_list.html'
    context = {
        'shop_with_dish_list': Shop.objects.all(),
        'dish_list': Dish.objects.all(),
    }
    return render(request, template_name, context)


def show_order(request):
    if not request.session.get('is_login', None):
        messages.warning(request, "请先登录顾客账户")
        return redirect('/customer/login/')
    template_name = 'dish/my_order.html'
    user_id = request.session['user_id']
    context = {
        'order_list': Orders.objects.filter(customer_id=user_id),
    }
    return render(request, template_name, context)


def get_order(request, dish_id):
    dish = get_object_or_404(Dish, dish_id=dish_id)
    user_id = request.session['user_id']
    try:
        user = Customer.objects.filter(customer_id=user_id).first()
        order = Orders.objects.create(dish=dish, customer=user)
        order.order_price = order.dish.dish_price
        order.order_status = 0
        order.save()
        messages.success(request, '下单成功，订单号为 (Order ID-{})，已支付 {} 元'.format(order.order_id, order.order_price))
        return redirect("dish:show_order")
    except ObjectDoesNotExist:
        messages.warning(request, "你目前还没有订单")
        return redirect("dish:show_order")


def review_order(request, dish_id):
    user_id = request.session['user_id']
    order = Orders.objects.get(dish_id=dish_id, customer_id=user_id, order_status=0)
    if request.method == "POST":
        comment_detail = request.POST.get('comment_detail', '')
        comment_score = request.POST.get('comment_score', '')
        comment_time = datetime.now()
        comment = Comments.objects.create(order_id=order.order_id, comment_detail=comment_detail, comment_score=comment_score, comment_time=comment_time)
        order.order_status = 1
        order.save()
        messages.success(request, '订单已完成，感谢您的评价！')
        return redirect("dish:show_order")
    else:
        return render(request, 'dish/review_order.html', {'order': order})