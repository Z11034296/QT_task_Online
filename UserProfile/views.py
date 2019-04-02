from django.shortcuts import render,HttpResponse,redirect,Http404,get_object_or_404
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from UserProfile.models import *
from UserProfile import forms
# Create your views here.


@csrf_exempt
def login(request):
    error_msg=""
    # 若POST 校验用户名密码
    if request.method == "POST":
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        user = auth.authenticate(username=username, password=pwd)
        if user:
            # 用户名密码正确
            # 给用户做登录
            auth.login(request, user)
            return redirect("userinfo")
        else:
            # 用户名密码错误
            error_msg = "用户名或密码错误"
            return render(request, "login.html", {"error": error_msg})
    return render(request, "login.html")


@csrf_exempt
def userinfo(request):
    if request.method == "GET":
        # 取所有單位：user_list傳給下級

        user_list_active = UserInfo.objects.filter(is_active=1)
        return render(request, "user/userinfo.html", {"user_list": user_list_active,"i": "0"})
    else:
        user_list_all = UserInfo.objects.all()
        return render(request, "user/userinfo.html", {"user_list": user_list_all, "i": "1"})

@csrf_exempt
def add_user(request):

    # 若為POST
    if request.method == "POST":
        # 從提交數據中拿到用戶填入數據
        add_user_obj = forms.UserForm(request.POST)
        if add_user_obj.is_valid():
            add_user_obj.cleaned_data.pop("re_password")
            UserInfo.objects.create_user(**add_user_obj.cleaned_data, first_name=request.POST.get('name'))
            return redirect("userinfo")
        return render(request, 'user/add_user.html', {'add_user_obj': add_user_obj})
    else:
        add_user_obj = forms.UserForm()
        return render(request, 'user/add_user.html', {'add_user_obj': add_user_obj})


def logout(request):
    # 注銷session
    auth.logout(request)
    return redirect("login")


@csrf_exempt
def update_userinfo(request, id):
    # 修改用戶信息
    if request.method == "GET":
        # 取ID
        if id:
            user_id = UserInfo.objects.filter(id=id).values().first()
            info_form = forms.UpdateUserForm(user_id)
            return render(request, "user/update_userinfo.html", {"info_form": info_form, "id": id})
        else:
            return HttpResponse("error")
    else:
        if id:
            # 获取修改信息
            update_obj = forms.UpdateUserForm(request.POST)
            if update_obj.is_valid():
                UserInfo.objects.filter(id=id).update(**update_obj.cleaned_data,
                                                      first_name=request.POST.get('name'))
                return redirect("userinfo")
            else:
                return HttpResponse("error")
        else:
            return HttpResponse("error")


def change_status(request, id):
    if request.method == "GET":
        # 取ID
        if id:
            user_info = get_object_or_404(UserInfo, id=id)
            return render(request, "user/change_status.html", {"userinfo": user_info})
        else:
            return HttpResponse("id_get error")
    else:
        if id:
            # 修改 is_active 为0
            user_status = get_object_or_404(UserInfo, id=id)
            user_status.is_active = 0
            user_status.leave_time = request.POST.get("leave_time")
            user_status.save()
            return redirect("userinfo")
        else:
            return HttpResponse("update_id_POST error")


# 修改密码
def set_password(request):
    user = request.user
    err_msg = ''
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        repeat_password = request.POST.get('repeat_password', '')
        # 检查旧密码是否正确
        if user.check_password(old_password):
            if not new_password:
                err_msg = '新密码不能为空'
            elif new_password != repeat_password:
                err_msg = '新密码两次输入不一致'
            else:
                user.set_password(new_password)
                user.save()
                logout(request)
                return redirect("login")
        else:
            err_msg = '旧密码输入错误'
    content = {
        'err_msg': err_msg,
    }
    return render(request, 'user/set_password.html', content)


def home(request, id):
    if request.method == "GET":
        if id:
            user_id = UserInfo.objects.filter(id=id).values().first()
            info_form = forms.UpdateUserForm(user_id)
            return render(request, "user/home.html", {"info_form":info_form, "id":id})
        else:
            return HttpResponse("error")
    else:
        if id:
            # 获取修改信息
            update_obj = forms.UpdateUserForm(request.POST)
            if update_obj.is_valid():
                UserInfo.objects.filter(id=id).update(**update_obj.cleaned_data,first_name=request.POST.get('name'))
                return redirect("userinfo")
            else:
                return HttpResponse("error")
        else:
            return HttpResponse("error")
