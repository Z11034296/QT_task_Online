from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from Project.forms import *
from Project import models
import TestCase.models as T
import UserProfile.models as U
from collections import Counter
from itertools import chain


def index(request):
    return render(request, 'Project/index.html')


def projects(request):
    result = models.Project.objects.all()
    #搜索此project是否已经有了Control table
    CT_lists = models.ControlTableList.objects.values('project_id')
    CT_list=[]
    for i in CT_lists:
        CT_list.append(i['project_id'])
    if request.method == "GET":
        return render(request, 'Project/projects.html', {'projects': result,'CT_list':CT_list})


def add_project(request):
    if request.method == "GET":
        obj = ProjectForm()
        return render(request, 'Project/add_project.html', {'obj': obj})
    else:
        obj = ProjectForm(request.POST)
        if obj.is_valid():
            p = models.Project.objects.create(**obj.cleaned_data)
            # 创建project 的同时创建一个对应的project_info
            pf = models.ProjectInfo(project_id=p.id)
            pf.save()
            return redirect('projects')
        return render(request, 'Project/add_project.html', {'obj': obj})


def edit_project(request, nid):
    if request.method == "GET":
        ret = models.Project.objects.filter(id=nid).values().first()
        obj = update_ProjectForm(ret)
        return render(request, 'Project/edit_project.html', {'nid': nid, 'obj': obj})
    else:
        obj = update_ProjectForm(request.POST)
        if obj.is_valid():
            models.Project.objects.filter(id=nid).update(**obj.cleaned_data)
            return redirect('projects')
        return render(request, 'Project/edit_project.html', {'nid': nid, 'obj': obj})


def project_info(request, nid):
    if request.method == "GET":
        ret = models.ProjectInfo.objects.filter(id=nid).values().first()
        obj_info = ProjectInfoForm(ret)
        return render(request, 'Project/project_info.html', {'nid': nid, 'obj_info': obj_info})
        # return HttpResponse('aaa')


def add_project_info(request, nid):
    pass


def edit_project_info(request, nid):
    if request.method == "GET":
        ret = models.ProjectInfo.objects.filter(project_id=nid).values().last()
        obj_info = ProjectInfoForm(ret, nid)
        return render(request, 'Project/edit_project_info.html', {'nid': nid, 'obj_info': obj_info})
    else:
        obj_info = ProjectInfoForm(request.POST, nid)
        if obj_info.is_valid():
            # models.ProjectInfo.objects.filter(id=nid).update(**obj_info.cleaned_data)
            models.ProjectInfo.objects.create(**obj_info.cleaned_data)
        return redirect('projects')


def create_project_info(request):
    models.ProjectInfo.objects.create({})


def test(request):
    return HttpResponse("Hello")


def project_ct(request,lid):
    if request.method == "GET":
        # 通过 Control table list id取到相关联project 信息
        plist=models.ControlTableList.objects.filter(id=lid).values().first()
        pj=models.Project.objects.filter(id=plist["project_id"]).values().first()

        # 将sheet list以及SKU num数量传给前端画出table

        sheets_list = T.Sheet.objects.all()
        case_list = T.TestCase.objects.all()
        test_user = U.UserInfo.objects.filter(site_id="1")
        SKU_Num_list = []
        num = 1
        while num <= int(pj['project_sku_qty']):
            SKU_Num_list.append(num)
            num += 1

        # 计算case_list中每个sheet有多少个case
        sheet_list = []
        for cases in case_list:
            sheet_list.append(cases.sheet.sheet_name)
        cout = Counter(sheet_list)

        # 每个sheet中的case个数填入sheets_list
        for sheets in sheets_list:
            sheets.count = cout[sheets.sheet_name]

        return render(request,'Project/project_ct.html',{"pj":pj,"plist":plist,
                                                         "SKU_Num_list":SKU_Num_list,
                                                         "sheets_list":sheets_list,"test_user":test_user})
    else:

        plist = models.ControlTableList.objects.filter(id=lid).values().first()
        pj = models.Project.objects.filter(id=plist["project_id"]).values().first()

        SKU_Num_list = []
        num = 1
        while num <= int(pj['project_sku_qty']):
            SKU_Num_list.append(num)
            num += 1

        sheets_list = T.Sheet.objects.all()
        for sheets in sheets_list:
            for i in SKU_Num_list:
                name = '{}-SKU{}'.format(sheets.id, i)
                tester=U.UserInfo.objects.filter(id=request.POST.get(name)).values().first()
                models.ControlTableContent.objects.create(sku_num=i,ControlTable_List_id_id=lid,
                                                               sheet_id_id=sheets.id,tester_id=tester["id"])
        return redirect('projects')


def project_ct_info(request,nid):

    CT_list = models.ControlTableList.objects.filter(project_id=nid)
    pj = models.Project.objects.filter(id=nid).values().first()
    ct_list = models.ControlTableContent.objects.values("ControlTable_List_id_id").distinct()
    ct_list_distinct=[]
    for i in ct_list:
        ct_list_distinct.append(i["ControlTable_List_id_id"])

    return render(request, 'Project/project_ct_info.html', {"CT_list":CT_list, "pj":pj,"ct_list_distinct":ct_list_distinct})

    # pj = models.Project.objects.filter(id=nid).values().first()
    # # 从control table库中查找关联project的sheet list
    #
    # sheet=models.ControlTable.objects.filter(project_name_id=nid).values().first()
    # l=sheet["control_table_sheet"]
    # l_new = l.replace("'", "").strip("[]").strip().split(',')  # 去掉空格和[]以及单引号，并以逗号分隔后生成一个list。
    # sheet_list = T.Sheet.objects.none()
    # sheets_list = []
    # for i in l_new:
    #     sheets = T.Sheet.objects.filter(id=i)
    #     sheets_list.append(sheets)
    # for i in sheets_list:
    #     sheet_list = sheet_list | i
    #
    # sheets_list=chain(sheet_list)
    # return render(request,'Project/project_ct_info.html',{"pj":pj,'sheet_list':sheets_list})


def project_ct_list(request,nid):

    if request.method == "GET":
        pj = models.Project.objects.filter(id=nid).values().first()
        return render(request,'Project/project_ct_list.html',{"pj":pj})
    else:
        result= request.POST
        pj = models.Project.objects.filter(id=nid).values().first()
        result_list = list(models.ControlTableList.objects.values_list('project_id', 'project_stage'))
        project_id = request.POST.get("project_id")
        project_stage = request.POST.get("project_stage")
        if (int(project_id),project_stage) in result_list:
            error='该project已经有这个stage了'
            return render(request, 'Project/project_ct_list.html', {"pj":pj,'error':error})
        models.ControlTableList.objects.create(project_stage=result["project_stage"],project_id=result["project_id"],
                                               stage_begin=result["stage_begin"],stage_end=result["stage_end"])
        return redirect('projects')


def project_ct_content(request,lid):
    plist = models.ControlTableList.objects.filter(id=lid).values().first()
    pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
    sheets_list = T.Sheet.objects.all()
    case_list = T.TestCase.objects.all()
    SKU_Num_list = []
    num = 1
    while num <= int(pj['project_sku_qty']):
        SKU_Num_list.append(num)
        num += 1

    # 计算case_list中每个sheet有多少个case
    sheet_list = []
    for cases in case_list:
        sheet_list.append(cases.sheet.sheet_name)
    cout = Counter(sheet_list)

    # 每个sheet中的case个数填入sheets_list
    for sheets in sheets_list:
        sheets.count = cout[sheets.sheet_name]
    content_list = models.ControlTableContent.objects.filter(ControlTable_List_id=lid)
    ziplist=zip(sheets_list,content_list)
    return render(request, 'Project/project_ct_content.html', {"pj": pj, "plist": plist,
                                                       "SKU_Num_list": SKU_Num_list,
                                                       "sheets_list": sheets_list,
                                                       "content_list":content_list,"ziplist":ziplist})
