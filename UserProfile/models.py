from django.db import models
from django.contrib.auth.models import User,AbstractUser
# Create your models here.


class UserInfo(User):
    """
    用户信息表----AbstractUser
    """
    name = models.CharField(max_length=32,null=True,unique=False) # 姓名
    job_name = models.CharField(max_length=24,null=True,unique=False) # 英文名
    gender = models.CharField(max_length=8,null=True,unique=False)
    avatar = models.FileField(upload_to="media/upload", default="media/upload/favicon.ico", verbose_name="头像") # 头像
    shot_number = models.CharField(max_length=11, null=True, unique=False) # 短号
    phone_number = models.CharField(max_length=11, null=True, unique=False) # 手机长号
    belone_to_team = models.ForeignKey("Team",null=True,on_delete=None) # 归属team
    # belone_to_team = models.CharField(max_length=32,null=True,unique=False) # 归属team
    university = models.CharField(max_length=255, null=True, unique=False) # 毕业学校
    major = models.CharField(max_length=255, null=True, unique=False) # 学校专业
    role = models.ForeignKey("Role", null=True, unique=False,on_delete=None)    # 权限外键
    join_in_time = models.DateField(null=True) # 入职时间
    leave_time = models.DateField(null=True) # 离职时间
    site = models.ForeignKey("Site", on_delete=models.CASCADE, blank=True, null=True)
    # 用户在职状态  : auth_user/is_active

    def __str__(self):
        return self.name


class Team(models.Model):
    """
    组别表
    """
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32,null=False,unique=False) # 组别名称
    team_leader = models.CharField(max_length=32,null=True,unique=False) # 外键

    def __str__(self):
        return self.name


class Menu(models.Model):
    """
    角色菜单表
    """
    name = models.CharField(max_length=32)
    url_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=64,null=False,unique=False)

    def __str__(self):
        return self.name


class Site(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name
