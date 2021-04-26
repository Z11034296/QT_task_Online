from django.db import models
import uuid,os
# Create your models here.

#
# def test_plan_pic_path(filename):
#     ext = filename.split('.')[-1]
#     filename = '{}.{}'.format(uuid.uuid4().hex[:8], ext)
#     sub_folder = 'file'
#     if ext.lower() in ["jpg", "png", "gif"]:
#         sub_folder = "pic"
#     if ext.lower() in ["pdf", "docx"]:
#         sub_folder = "document"
#     return os.path.join("/TestCase/upload", sub_folder, filename)


class TestCase(models.Model):
    case_id=models.CharField(max_length=64,null=False,unique=True)  #
    case_name=models.CharField(max_length=255,null=False,unique=False)  #
    function=models.ForeignKey("Function",null=True,on_delete=None)  # 归属function
    sheet=models.ForeignKey("Sheet",null=True,on_delete=None)  # 归属sheet
    procedure=models.TextField(blank=True, null=True,)  # 步骤
    pass_criteria=models.TextField(blank=True, null=True,)  # pass标准
    test_plan_pic_path=models.FileField(upload_to='upload',blank=True, null=True,)  # 附件路径
    attend_time=models.CharField(max_length=128,null=False,unique=False,default='0')  #
    unattend_time=models.CharField(max_length=128,null=False,unique=False,default='0')  #
    case_note=models.CharField(max_length=512,null=False,unique=False,default='') # Note
    case_status=models.CharField(max_length=32,null=False,unique=False,default='1')# status

    def __str__(self):
        return self.case_name


class Function(models.Model):
    function_name=models.CharField(max_length=64,null=True,unique=True)

    def __str__(self):
        return self.function_name


class Sheet(models.Model):
    sheet_name = models.CharField(max_length=128,null=False,unique=True)
    sheet_description = models.CharField(max_length=128,null=True,unique=False)
    sheet_prepare = models.TextField(blank=True, null=True,)
    attend_time = models.CharField(max_length=128, unique=False, verbose_name="attend_time", null=True, default="0")
    sorting = models.CharField(max_length=128,null=True,unique=False)
    evt = models.CharField(max_length=128,null=True,unique=False)
    dvt = models.CharField(max_length=128,null=True,unique=False)
    Consumer = models.CharField(max_length=128,null=True,unique=False)
    Commercial = models.CharField(max_length=128,null=True,unique=False)



    def __str__(self):
        return self.sheet_name

class TestPlan_RN(models.Model):
    rn_version = models.CharField(max_length=128,null=False,unique=True,verbose_name="rn_version")
    rn_date = models.DateField(blank=True, null=True)
    rn_description = models.TextField(blank=True, null=True,verbose_name="rn_description")
    rn_keeper = models.CharField(max_length=128, unique=False, verbose_name="rn_keeper", null=True,)
    rn_mote = models.TextField(blank=True, null=True,)



    def __str__(self):
        return self.rn_version


