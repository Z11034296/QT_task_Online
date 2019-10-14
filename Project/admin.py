from django.contrib import admin
from Project.models import *
# Register your models here.


class PlatformAdmin(admin.ModelAdmin):
    list_display = ('id','name')


admin.site.register(Platform, PlatformAdmin)


class FamilyAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    


admin.site.register(ProjectType, FamilyAdmin)


class TypeAdmin(admin.ModelAdmin):
    list_display = ('id','name')


admin.site.register(ProjectStyle, TypeAdmin)