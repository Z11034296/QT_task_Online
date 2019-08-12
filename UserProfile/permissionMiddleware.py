
from django.utils.deprecation import MiddlewareMixin
import re
from django.shortcuts import HttpResponse,redirect,render


class validPermission(MiddlewareMixin):

    def process_request(self,request):
        # 当前访问路径
        current_path = request.path_info
        # print(current_path)
        # 检查是否属于白名单
        valid_url_list=["/login/","/admin/.*","/user/login","/index/"]

        for valid_url in valid_url_list:
            ret=re.match(valid_url,current_path)
            if ret:
                return None

        # 校验是否登录
        user_id=request.session.get("user_id")
        if not user_id:
            return redirect("/login/")

        # 校验权限
        permission_list = request.session.get("permission_list",[])
        # print(permission_list)
        flag = False
        for permission in permission_list:

            permission = "^%s$" % permission

            ret = re.match(permission, current_path)
            if ret:
                flag = True
                break
        if not flag:
            return render(request,"nopermission.html")
            # return HttpResponse("无权访问！")

        return None