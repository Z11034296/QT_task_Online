"""onlinesytem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from Project import views

urlpatterns = [
    path('', views.index, name='index'),

    path('projects', views.projects, name='projects'),
    path('add_project', views.add_project, name='add_projects'),
    path('edit_project/<int:nid>/', views.edit_project, name='edit_projects'),
    path('project_info/<int:nid>/', views.project_info, name='project_info'),
    path('add_project_info/<int:nid>/', views.add_project_info, name='add_project_info'),
    path('edit_project_info/<int:nid>/', views.edit_project_info, name='edit_project_info'),
    path('test', views.test, name='test'),
    path('project_ct/<lid>', views.project_ct, name='project_ct'),
    path('project_ct_info/<int:nid>', views.project_ct_info, name='project_ct_info'),
    path('project_ct_list/<nid>', views.project_ct_list, name='project_ct_list'),
    path('project_ct_content/<lid>', views.project_ct_content, name='project_ct_content'),
    path('test_result/<lid>-<sid>-<skunum>', views.test_result, name='test_result'),
    path('task_table/<lid>', views.task_table, name='task_table'),
    path('task_list', views.task_list, name='task_list'),
    path('result_review/<lid>-<sid>-<skunum>', views.result_review, name='result_review'),
]
