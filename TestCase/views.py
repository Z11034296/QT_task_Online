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
    paginator = Paginator(case_list_org, 15, 1)  # 每页9条结果，少于1条合并到上一页


    page_num = request.GET.get('page')
    try:
        case_list = paginator.page(page_num)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        case_list = paginator.page(1)
        page_num = 1

    except EmptyPage:
        # 当参数页码大于或小于页码范围时,会触发该异常
        if int(page_num) > paginator.num_pages:
            # 大于 获取最后一页数据返回
            case_list = paginator.page(paginator.num_pages)
        else:
            # 小于 获取第一页
            case_list = paginator.page(1)
    page_sumrange = range(1,paginator.num_pages+1)
    page_num = int(page_num)
    if page_num < 4:
        if paginator.num_pages <= 7:
            dis_range = range(1, paginator.num_pages + 1)
        else:
            dis_range = range(1, 8)
    elif (page_num >= 4) and (page_num <= paginator.num_pages-3):
        dis_range = range(page_num - 3,page_num+4)
    else:
        dis_range = range(paginator.num_pages - 6, paginator.num_pages+1)

    return render(request, "case/caseinfo.html",
                  {'case_list': case_list, 'paginator': paginator, 'dis_range': dis_range,"page_sumrange":page_sumrange})


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
    sheet_info = {
        "MST01":	1 ,
        "Drv01":	2 ,
        "Aud01":	3 ,
        "Aud01a":	4 ,
        "Aud01b":	5 ,
        "Aud01c":	6 ,
        "Aud01d":	7 ,
        "Aud01e":	8 ,
        "Aud01f":	9 ,
        "Aud02":	10 ,
        "Vdo01":	11 ,
        "Vdo01a":	12 ,
        "Vdo01b":	13 ,
        "Vdo01c":	14 ,
        "Vdo01d":	15 ,
        "Vdo01e":	16 ,
        "Vdo01f":	17 ,
        "Vdo01g":	18 ,
        "Vdo01h":	19 ,
        "Vdo01j":	20 ,
        "Vdo01k":	21 ,
        "Vdo02":	22 ,
        "Vdo03":	23 ,
        "Vdo04":	24 ,
        "Vdo05":	25 ,
        "Vdo06":	26 ,
        "Vdo07":	27 ,
        "Vdo08":	28 ,
        "Vdo09":	29 ,
        "Vdo10":	30 ,
        "Vdo11":	31 ,
        "Vdo12":	32 ,
        "SW01":	    33 ,
        "SW02":	    34 ,
        "SW03":	    35 ,
        "SW05":	    36 ,
        "SW07":	    37 ,
        "SW09":	    38 ,
        "HW01":	    39 ,
        "HW01a":	40 ,
        "HW01b":	41 ,
        "HW01c":	42 ,
        "HW01d":	43 ,
        "HW01e":	44 ,
        "HW01f":	45 ,
        "HW01g":	46 ,
        "HW01h":	47 ,
        "HW01i":	48 ,
        "HW02a":	49 ,
        "HW02b":	50 ,
        "HW02c":	51 ,
        "HW02d":	52 ,
        "HW02e":	53 ,
        "HW02f":	54 ,
        "HW02g":	55 ,
        "HW04":	    56 ,
        "HW05":	    57 ,
        "HW06":	    58 ,
        "HW07":	    59 ,
        "NET01":	60 ,
        "NET02":	61 ,
        "NET03":	62 ,
        "NET06":	63 ,
        "NET07":	64 ,
        "MEM01":	65 ,
        "USB01":	66 ,
        "USB02":	67 ,
        "USB03":	68 ,
        "TV01":	    69 ,
        "FNC01a":	70 ,
        "FNC01b":	71 ,
        "FNC01c":	72 ,
        "FNC02":	73 ,
        "B1.1":	    74 ,
        "FNC01":	75 ,
        "MEM02":	76 ,
        "FNC03":	77 ,
        "FNC04":	78 ,
        "FNC05":	79 ,
        "FNC06":	80 ,
        "FNC07":	81 ,
        "FNC08":	82 ,
        "FNC09":	83 ,
        "FNC10":	84 ,
        "FNC11":	85 ,
        "FNC12":	86 ,
        "FNC13":	87 ,
        "FNC14":	88 ,
        "FNC15":	89 ,
        "FNC17":	90 ,
        "FNC18":	91 ,
        "FNC19":	92 ,
        "FNC20":	93 ,
        "FNC21":	94 ,
        "FNC27":	95 ,
        "FNC31":	96 ,
        "FNC33":	97 ,
        "FNC35":	98 ,
        "FNC61":	99 ,
        "FNC37":	100 ,
        "FNC38":	101 ,
        "FNC39":	102 ,
        "FNC40":	103 ,
        "FNC41":	104 ,
        "FNC42":	105 ,
        "FNC44":	106 ,
        "FNC46":	107 ,
        "FNC47":	108 ,
        "FNC48":	109 ,
        "FNC49":	110 ,
        "FNC50":	111 ,
        "FNC51":	112 ,
        "FNC52":	113 ,
        "FNC53":	114 ,
        "FNC54":	115 ,
        "FNC55":	116 ,
        "FNC56":	117 ,
        "FNC57":	118 ,
        "FNC58":	119 ,
        "FNC60":	120 ,
        "B1.2":	    122 ,
        "B1.3":	    123 ,
        "B1.4":	    124 ,
        "B1.5":	    125 ,
        "B5":	    129 ,
        "B6":	    130 ,
        "B7":	    131 ,
        "B9":	    133 ,
        "B10":	    134 ,
        "B11":  	135 ,
        "B12":	    136 ,
        "B13":  	137 ,
        "B15":  	138 ,
        "B18":	    140 ,
        "B19":  	141 ,
        "B19.2":	142 ,
        "B20":	    143 ,
        "P1":	    144 ,
        "UXP01":	145 ,
        "UXP02":	146 ,
        "UXP03":	147 ,
        "W1":	    148 ,
        "W2":	    149 ,
        "W3":	    150 ,
        "W4":	    151 ,
        "W6":	    152 ,
        "W7":   	153 ,
        "W8":	    154 ,
        "W9":	    155 ,
        "L1":	    156 ,
        "EC":	    157 ,
        "Vdo13":	158 ,
        "FNC29":	159 ,
        "MEM03":	160 ,
        "MST02":	161 ,
        "HW02": 	162 ,
        "B2":	    163 ,
        "B3":	    164 ,
        "B4":	    165 ,



    }
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
                                            procedure=rowVlaues[2],
                                            pass_criteria=rowVlaues[3],
                                            attend_time=int(rowVlaues[5]),
                                            unattend_time=int(rowVlaues[6]),
                                            function_id=int(rowVlaues[9]),
                                            sheet_id=sheet_info[rowVlaues[8]],
                                            case_status=int(rowVlaues[7]),
                                            case_note=rowVlaues[4],
                                            )
                except:
                    return HttpResponse("excel文件或者数据插入错误")
            return redirect("table_of_contents")
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
    sheet_id = TestCase.objects.filter(id=id).values('sheet_id').first()["sheet_id"]
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
                    return redirect('sheet_detail',sheet_id)
            else:
                update_obj = forms.Case_updateForm(request.POST)
                if update_obj.is_valid():
                    dic=update_obj.cleaned_data
                    dic.pop('test_plan_pic_path')
                    TestCase.objects.filter(id=id).update(**dic)
                    return redirect('sheet_detail', sheet_id)
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
    j=range(1,3)
    sheets_list = Sheet.objects.all().order_by("sorting")
    case_list = TestCase.objects.filter(case_status='1').all()
    # 计算case_list中每个sheet有多少个case
    sheet_list=[]
    for cases in case_list:
        sheet_list.append(cases.sheet.sheet_name)
    cout=Counter(sheet_list)
    # 每个sheet中的case个数填入sheets_list
    attend_time_dic = {}
    for sheets in sheets_list:
        # print(sheets.attend_time)
        sheets.count = cout[sheets.sheet_name]
        # 计算每个Sheet的attend time
        cases_by_sheet = TestCase.objects.filter(sheet_id=sheets.id,case_status='1').values('attend_time')
        attend_time_sum = 0
        for i in cases_by_sheet:
            attend_time_sum += float(i['attend_time'])
        attend_time_dic.update({sheets: attend_time_sum})
        sheets.attend_time = attend_time_dic[sheets]
        if sheets.attend_time != float(Sheet.objects.filter(id=sheets.id).values().first()['attend_time']):
            Sheet.objects.filter(id=sheets.id).update(attend_time=sheets.attend_time)

    return render(request, "case/table_of_contents.html", {"sheets_list": sheets_list,"j":j,"attend_time_dic":attend_time_dic})


def sheet_detail(request, sid):
    if request.method == "GET":
        case_list_by_sheet = TestCase.objects.filter(sheet_id=sid,case_status=1).order_by('case_id')
        sheet_prepare=Sheet.objects.filter(id=sid).values().first()['sheet_prepare']
        name = Sheet.objects.filter(id=sid).values().first()['sheet_name']
        return render(request, "case/sheet_case.html", {"case_list": case_list_by_sheet,"name":name,'sheet_prepare':sheet_prepare})


def search(request):
    error_msg = ''
    if request.method == "POST":
        if not request.POST.get('search_case'):
            error_msg = '请输入搜索词！！！'
            return render(request,'case/caseinfo.html', {'error_msg': error_msg})
        else:
            case_list = TestCase.objects.filter(case_name__contains=request.POST.get('search_case'))
            if not case_list:
                error_msg = '没有搜索到符合条件的内容！！！'

            return render(request, 'case/caseinfo.html',{'case_list': case_list, 'error_msg': error_msg})