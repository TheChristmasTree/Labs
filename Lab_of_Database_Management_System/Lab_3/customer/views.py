# Create your views here.

from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm
from django.contrib import messages
from .models import Customer
from dish.models import Dish

def register(request):
    register_form = RegisterForm()
    if request.session.get('is_login', None):
        return render(request, 'customer/index.html', locals())
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            tel = register_form.cleaned_data['tel']
            if password1 != password2:
                print("[DEBUG][POST][STATE]:两次输入的密码不同！")
                return render(request, 'customer/register.html', locals())
            else:
                same_id_cus = Customer.objects.filter(customer_name=username)
                if same_id_cus:
                    message = '该用户名已经存在，请换一个'
                    return render(request, 'customer/register.html', locals())
                else:
                    new_cus = Customer.objects.create(customer_name=username, customer_tel=tel,
                                                      customer_password=password1)
                    new_cus.save()
                    login_form = LoginForm()
                    message = "注册成功！"
                    return render(request, 'customer/login.html', locals())
    else:
        return render(request, 'customer/register.html', locals())
    return render(request, 'customer/register.html', locals())


def login(request):
    login_form = LoginForm()
    if request.session.get('is_login', None):
        print("[DEBUG][POST][STATE]:已登陆")
        return render(request, 'customer/index.html', locals())
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            print("[DEBUG][POST][LOGIN][username]:{}".format(username))
            print("[DEBUG][POST][LOGIN][password]:{}".format(password))
            try:
                print("[DEBUG][POST][STATE]:查询顾客用户数据库")
                user_cus = Customer.objects.get(customer_name=username)
                if user_cus.customer_password == password:
                    print("[DEBUG][POST][USERNAME]:{}".format(user_cus.customer_name))
                    print("[DEBUG][POST][STATE]:登录成功")
                    messages.success(request, '{}登录成功！'.format(user_cus.customer_name))
                    user_cus.customer_status = 1
                    user_cus.save()
                    request.session['is_login'] = True
                    request.session['user_id'] = user_cus.customer_id
                    request.session['user_name'] = user_cus.customer_name
                    request.session['tel'] = user_cus.customer_tel
                    return render(request, 'customer/index.html', locals())
                else:
                    print("[DEBUG][POST][STATE]:密码不正确")
                    message = "密码不正确"
            except:
                print("[DEBUG][POST][STATE]:用户不存在")
                message = "用户不存在"
    return render(request, 'customer/login.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return render(request, 'customer/index.html', locals())
    user_id = request.session['user_id']
    print("[DEBUG][REQUEST][退出]]")
    print("[DEBUG][REQUEST][USER_ID]:{}".format(user_id))
    try:
        user = Customer.objects.get(customer_id=user_id)
        print("[DEBUG][REQUEST][退出]]：退出顾客登陆状态")
        user.customer_status = 0
        user.save()
    except:
        print("[DEBUG][request][STATE]:退出错误，无法更新数据库中用户状态")
    request.session.flush()
    return render(request, 'customer/index.html', locals())


def information(request):
    if not request.session.get('is_login', None):
        messages.warning(request, "请先登录顾客账户")
        return redirect('/customer/login/')
    user_id = request.session['user_id']
    customer = Customer.objects.filter(customer_id=user_id).first()
    return render(request, 'customer/information.html', locals())


def show_info(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        tel = request.POST.get('tel')
        user_id = request.session['user_id']
        customer = Customer.objects.filter(customer_id=user_id).first()
        same_id_cus = Customer.objects.filter(customer_name=username).exclude(customer_id=user_id)
        if same_id_cus:
            messages.warning(request, '该用户名已经存在，请换一个')
            return render(request, 'customer/show_info.html')
        if not username or not password:
            messages.warning(request, '用户名和密码不能为空')
            return render(request, 'customer/show_info.html')
        if not tel:
            messages.warning(request, '电话号码不能为空')
            return render(request, 'customer/show_info.html')
        if len(tel) != 11 or not tel.isdigit():
            messages.warning(request, '电话号码必须为11位数字')
            return render(request, 'customer/show_info.html')
        customer.customer_name = username
        customer.customer_password = password
        customer.customer_tel = tel
        customer.save()
        messages.success(request, '个人信息更新成功！')

    return render(request, 'customer/show_info.html')


def index(request):
    dish_list = Dish.objects.exclude(dish_score=None).order_by('-dish_score')
    return render(request, 'customer/index.html', {'dishes': dish_list})