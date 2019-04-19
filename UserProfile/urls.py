from django.contrib import admin
from django.urls import path
from . import views
import Project.views


urlpatterns = [

    path('userinfo', views.userinfo, name='userinfo'),
    path('add_user', views.add_user, name='add_user'),
    path('login', views.logout, name='logout'),
    path('update_userinfo/<id>', views.update_userinfo, name='update_userinfo'),
    path('change_status/<id>', views.change_status, name='change_status'),
    path('set_password', views.set_password, name='set_password'),
    path('home/<id>', views.home, name='home'),
    path('task_list',  Project.views.task_list, name='task_list'),

]
