from django.shortcuts import render,HttpResponse,redirect,Http404,get_object_or_404
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from TestCase.models import *
from TestCase import forms
import os,uuid,time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import xlrd  # 需额外安装 xlrd <!-- pip install xlrd -->
from collections import Counter
# Create your views here.


def caseinfo(request):
    # 取所有單位：case_list并以Case_id排序
    # case_list = TestCase.objects.all()

    case_list_org = TestCase.objects.order_by('case_id').filter()
    paginator = Paginator(case_list_org, 9, 1)  # 每页10条结果，少于2条合并到上一页

    page = request.GET.get('page')
    try:
        case_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        case_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        case_list = paginator.page(paginator.num_pages)
    return render(request, "case/caseinfo.html", {"case_list": case_list})


@csrf_exempt
def add_case(request):
    if request.method == "POST":# 從提交數據中拿到用戶填入數據
        if request.FILES:
            add_case_obj = forms.CaseForm(request.POST, request.FILES)
            filename_org = request.FILES.get("test_plan_pic_path").name
            ext = filename_org.split('.')[-1]
            filename_new = '{}.{}'.format(uuid.uuid4().hex[:8], ext)
            if add_case_obj.is_valid():
                dic = add_case_obj.cleaned_data
                dic['test_plan_pic_path'] = filename_new
                TestCase.objects.create(**dic)

                with open(os.path.join("media/upload",filename_new), 'wb+') as f:
                    for chunk in request.FILES.get("test_plan_pic_path").chunks():
                        f.write(chunk)
                return redirect("caseinfo")
        else:
            add_case_obj = forms.CaseForm(request.POST,request.FILES)
            if add_case_obj.is_valid():
                TestCase.objects.create(**add_case_obj.cleaned_data)
                return redirect("caseinfo")
        return render(request, 'case/add_case.html', {'add_case_obj': add_case_obj})
    else:
        add_case_obj = forms.CaseForm()
        return render(request, 'case/add_case.html', {'add_case_obj': add_case_obj})


'''文件上传'''


def upload_files(request):
    if request.method == 'POST':
        f = request.FILES.get('upload_files')
        excel_type = f.name.split('.')[1]
        if excel_type in ['xlsx', 'xls']:
            # 解析excel表格
            wb = xlrd.open_workbook(filename=None, file_contents=f.read())
            table = wb.sheets()[0]
            rows = table.nrows  # 总行数
            for i in range(1, rows):
                try:
                    rowVlaues = table.row_values(i)
                    TestCase.objects.create(case_id=rowVlaues[0],
                                            case_name=rowVlaues[1],
                                            procedure=rowVlaues[4],
                                            pass_criteria=rowVlaues[5],
                                            attend_time=int(rowVlaues[6]),
                                            function_id=int(rowVlaues[2]),
                                            sheet_id=int(rowVlaues[3]),
                                            case_status=int(rowVlaues[7]),
                                            case_note=rowVlaues[8],
                                            )
                except:
                    return HttpResponse("excel文件或者数据插入错误")
            return redirect("caseinfo")
        else:
            return HttpResponse('上传文件类型错误！')
    else:
        return render(request, 'case/upload_files.html')


@csrf_exempt
def delete_case(request, id):
    if request.method == "GET":
        # 取ID
        if id:
            case_info = get_object_or_404(TestCase, id=id)
            return render(request, "case/delete_case.html", {"caseinfo": case_info})
        else:
            return HttpResponse("case_id_get error")
    else:
        if id:
            # 修改 is_active 为0
            TestCase.objects.filter(id=id).delete()
            return redirect("caseinfo")
        else:
            return HttpResponse("delete_case error")


@csrf_exempt
def update_case(request, id):
    # 修改用戶信息
    if request.method == "GET":
        # 取ID
        if id:
            case_id = TestCase.objects.filter(id=id).values().first()
            case_info_obj = forms.Case_updateForm(case_id)
            return render(request, "case/update_case.html", {"case_info_obj": case_info_obj, "id": id})
        else:
            return HttpResponse("error")
    else:
        if id:
            if request.FILES:
                # 获取修改信息
                update_obj = forms.Case_updateForm(request.POST,request.FILES)
                filename_org = request.FILES.get("test_plan_pic_path").name
                ext = filename_org.split('.')[-1]
                filename_new = '{}.{}'.format(uuid.uuid4().hex[:16], ext)
                if update_obj.is_valid():
                    dic = update_obj.cleaned_data
                    dic['test_plan_pic_path'] = filename_new
                    TestCase.objects.filter(id=id).update(**dic)
                    with open(os.path.join("media/upload", filename_new), 'wb+') as f:
                        for chunk in request.FILES.get("test_plan_pic_path").chunks():
                            f.write(chunk)
                    return redirect("caseinfo")
            else:
                update_obj = forms.Case_updateForm(request.POST)
                if update_obj.is_valid():
                    dic=update_obj.cleaned_data
                    dic.pop('test_plan_pic_path')
                    TestCase.objects.filter(id=id).update(**dic)
                    return redirect("caseinfo")
        else:
            return HttpResponse("id error")


def case_moreinfo(request, id):
    # 查看case详细
    if request.method == "GET":
        # 取ID
        if id:
            case_id = TestCase.objects.filter(id=id).values().first()
            case_info_obj = forms.Case_updateForm(case_id)
            return render(request, "case/case_moreinfo.html", {"case_info_obj": case_info_obj, "id": id})
        else:
            return HttpResponse("error")


def table_of_contents(request):
    i=[1,2,3,4]
    sheets_list = Sheet.objects.all()
    case_list = TestCase.objects.all()
    # 计算case_list中每个sheet有多少个case
    sheet_list=[]
    for cases in case_list:
        sheet_list.append(cases.sheet.sheet_name)
    cout=Counter(sheet_list)
    # 每个sheet中的case个数填入sheets_list
    for sheets in sheets_list:
        sheets.count = cout[sheets.sheet_name]
    # paginator = Paginator(case_list_org, 9, 1)  # 每页10条结果，少于2条合并到上一页
    #
    #     # page = request.GET.get('page')
    #     # try:
    #     #     case_list = paginator.page(page)
    #     # except PageNotAnInteger:
    #     #     # If page is not an integer, deliver first page.
    #     #     case_list = paginator.page(1)
    #     # except EmptyPage:
    #     #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     #     case_list = paginator.page(paginator.num_pages)
    return render(request, "case/table_of_contents.html", {"sheets_list": sheets_list,"i":i})


def sheet_detail(request, sid):
    if request.method == "GET":
        case_list_by_sheet = TestCase.objects.filter(sheet_id=sid)
        name = Sheet.objects.filter(id=sid).values().first()['sheet_name']
        return render(request, "case/sheet_case.html", {"case_list": case_list_by_sheet,"name":name})