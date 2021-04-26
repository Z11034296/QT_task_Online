from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from TestCase import views
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    path('caseinfo', views.caseinfo, name='caseinfo'),
    path('add_case', views.add_case, name='add_case'),
    path('delete_case/<id>', views.delete_case, name='delete_case'),
    path('update_case/<id>', views.update_case, name='update_case'),
    path('case_moreinfo/<id>', views.case_moreinfo, name='case_moreinfo'),
    path('upload_files', views.upload_files, name='upload_files'),
    path('table_of_contents', views.table_of_contents, name='table_of_contents'),
    path('sheet_detail/<sid>', views.sheet_detail, name='sheet_detail'),
    path('search', views.search, name='search'),
    path('rn', views.rn, name='rn'),
    path('add_rn', views.add_rn, name='add_rn'),
]