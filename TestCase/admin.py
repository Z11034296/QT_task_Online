from django.contrib import admin
from TestCase.models import *


# Register your models here.

class SheetAdmin(admin.ModelAdmin):
    list_display = ('id','sheet_name','sheet_description','sorting')


admin.site.register(Sheet, SheetAdmin)