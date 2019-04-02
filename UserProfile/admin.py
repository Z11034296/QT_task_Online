from django.contrib import admin
from UserProfile.models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.


@admin.register(UserInfo)
class Userinfo(admin.ModelAdmin):

    list_display = ('id','username','name' ,'job_name','phone_number','belone_to_team',
                    'join_in_time','university','major','leave_time','last_login')


admin.register(UserInfo,UserAdmin)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_leader')


admin.site.register(Team, TeamAdmin)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Role, RoleAdmin)


