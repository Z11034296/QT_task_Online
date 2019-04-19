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
    # 搜索此project是否已经有了Control table
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


# ct == control table
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
        while num <= int(plist['stage_sku_qty']):
            SKU_Num_list.append(num)
            num += 1

        # 计算case_list中每个sheet有多少个case
        sheet_list = []
        for cases in case_list:
            sheet_list.append(cases.sheet.sheet_name)
        cout = Counter(sheet_list)

        # 每个sheet中的case个数填入sheets_list
        attend_time_dic={}
        for sheets in sheets_list:

            sheets.count = cout[sheets.sheet_name]

        # 计算每个Sheet的attend time
            cases_by_sheet = T.TestCase.objects.filter(sheet_id=sheets.id).values('attend_time')
            attend_time_sum = 0
            for i in cases_by_sheet:

                attend_time_sum+=int(i['attend_time'])
            attend_time_dic.update({sheets:attend_time_sum * int(plist['stage_sku_qty'])})
            sheets.attend_time=attend_time_dic[sheets]
        return render(request,'Project/project_ct.html',{"pj":pj,"plist":plist,
                                                         "SKU_Num_list":SKU_Num_list,
                                                         "sheets_list":sheets_list,"test_user":test_user,'attend_time_dic':attend_time_dic})
    else:

        plist = models.ControlTableList.objects.filter(id=lid).values().first()
        pj = models.Project.objects.filter(id=plist["project_id"]).values().first()

        SKU_Num_list = []
        num = 1
        while num <= int(plist['stage_sku_qty']):
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
        result_list = list(models.ControlTableList.objects.values_list('project_id', 'project_stage','stage_sku_qty'))
        project_id = request.POST.get("project_id")
        project_stage = request.POST.get("project_stage")
        stage_sku = request.POST.get("stage_sku_qty")
        if (int(project_id),project_stage) in result_list:
            error='该project已经有这个stage了'
            return render(request, 'Project/project_ct_list.html', {"pj":pj,'error':error})
        models.ControlTableList.objects.create(project_stage=result["project_stage"],project_id=result["project_id"],
                                               stage_sku_qty=stage_sku,stage_begin=result["stage_begin"],stage_end=result["stage_end"])
        return redirect('projects')


def project_ct_content(request,lid):
    plist = models.ControlTableList.objects.filter(id=lid).values().first()
    pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
    sheets_list = T.Sheet.objects.all()
    case_list = T.TestCase.objects.all()
    SKU_Num_list = []
    num = 1
    while num <= int(plist['stage_sku_qty']):
        SKU_Num_list.append(num)
        num += 1

    # 计算case_list中每个sheet有多少个case
    sheet_list = []
    for cases in case_list:
        sheet_list.append(cases.sheet.sheet_name)
    cout = Counter(sheet_list)

    # sheet的测试结果，若都Pass则Pass ，有一个fail则结果显示fail，若全部N/A 才写N/A，若有没有填结果的case则显示为空
    res_list = models.TestResult.objects.filter(ControlTableList_id=lid).values('sheet_id', 'test_result')
    sheet_result_list = {}

    for i in sheets_list:
        re_list = []
        final_result = ''
        for j in res_list:
            if i.id == int(j['sheet_id']):
                re_list.append(j['test_result'])
                if 'Fail' in re_list:
                    final_result = 'Fail'
                elif re_list == []:
                    final_result = ''
                else:
                    final_result = 'Pass'

        sheet_result_list[i.sheet_name] = final_result

    # 每个sheet中的case个数填入sheets_list
    attend_time_dic={}
    for sheets in sheets_list:
        sheets.count = cout[sheets.sheet_name]

        cases_by_sheet = T.TestCase.objects.filter(sheet_id=sheets.id).values('attend_time')
        attend_time_sum = 0
        for i in cases_by_sheet:
            attend_time_sum += int(i['attend_time'])
        attend_time_dic.update({sheets.id: attend_time_sum * int(plist['stage_sku_qty']) })

    content_list = models.ControlTableContent.objects.filter(ControlTable_List_id=lid)

    new_list=[]
    new_dic={}

    # 将每个sheet所有SKU信息整合到同个字典中方便使用
    count=0
    for i in content_list:
        count+=1

        new_dic.update({'sheet_id':i.sheet_id_id,'sheet_name':i.sheet_id.sheet_name,'attend_time':attend_time_dic[i.sheet_id_id],
                        'sheet_description':i.sheet_id.sheet_description})
        new_dic.update({'sku'+str(count % int(plist['stage_sku_qty'])):i.tester})

        if count % int(plist['stage_sku_qty']) == 0:
            new_dic.update({'sku' + str(int(plist['stage_sku_qty'])): i.tester,'test_result':sheet_result_list[i.sheet_id.sheet_name]})

            # new_list.append(new_dic) # 字典更新会让list同步更新，需要将整个字典赋值
            new_list.append(dict(new_dic))
    return render(request, 'Project/project_ct_content.html', {"pj": pj, "plist": plist,
                                                               "SKU_Num_list": SKU_Num_list,"new_list":new_list,})


def test_result(request,sid,lid,skunum):  # lid:Controltable_list_id , sid:sheet_id,
    if request.method == "GET":
        plist = models.ControlTableList.objects.filter(id=lid).values().first()
        pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
        cases = T.TestCase.objects.filter(sheet_id=sid)
        name = T.Sheet.objects.filter(id=sid).values().first()['sheet_name']
        return render(request, "Project/test_result.html", {"case_list": cases,"name":name,"pj":pj,"plist":plist,"skunum":skunum})
    else:

        # case id 与 result组成字典后加到数据库
        project = models.Project.objects.filter(id=lid).values('id').first()
        case_id_list=request.POST.getlist('case_id')
        result_list=request.POST.getlist('test_result')
        remark_list=request.POST.getlist('remark')
        result=dict(zip(case_id_list,result_list))
        remark_result=dict(zip(case_id_list,remark_list))
        result_info_id = models.ProjectInfo.objects.filter(project_id=project['id']).values("id").last()
        for i in result:
            models.TestResult.objects.create(ControlTableList_id=lid,sku_num=skunum,test_case_id=int(i),
                                             test_result=result[i],tester_id=request.user.id,sheet_id=sid,
                                             remark=remark_result[i],result_info_id = result_info_id['id'])
            # result_info_id = result_info_id['id']
        return redirect('task_table',lid=lid)


def task_table(request,lid):
    plist = models.ControlTableList.objects.filter(id=lid).values().first()
    pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
    sheets_list = T.Sheet.objects.all()
    case_list = T.TestCase.objects.all()
    SKU_Num_list = []
    num = 1
    while num <= int(plist['stage_sku_qty']):
        SKU_Num_list.append(num)
        num += 1

    # 计算case_list中每个sheet有多少个case
    sheet_list = []
    for cases in case_list:
        sheet_list.append(cases.sheet.sheet_name)
    cout = Counter(sheet_list)

    # sheet的测试结果，若都Pass则Pass ，有一个fail则结果显示fail，若全部N/A,才写N/A，若有没有填结果的case则显示为空
    res_list = models.TestResult.objects.filter(ControlTableList_id=lid).values('sheet_id', 'test_result')
    sheet_result_list = {}

    for i in sheets_list:

        re_list = []
        final_result = ''
        for j in res_list:
            if i.id == int(j['sheet_id']):
                re_list.append(j['test_result'])
        if 'Fail' in re_list:
            final_result='Fail'
        elif re_list==[]:
            final_result=''
        elif re_list != [] and 'Pass' not in re_list and 'Fail' not in re_list :
            final_result = 'N/A'
        else:
            final_result = 'Pass'

        sheet_result_list[i.sheet_name] = final_result

    # 每个sheet中的case个数填入sheets_list
    attend_time_dic={}
    for sheets in sheets_list:
        sheets.count = cout[sheets.sheet_name]

        cases_by_sheet = T.TestCase.objects.filter(sheet_id=sheets.id).values('attend_time')
        attend_time_sum = 0
        for i in cases_by_sheet:
            attend_time_sum += int(i['attend_time'])
        attend_time_dic.update({sheets.id: attend_time_sum * int(plist['stage_sku_qty'])})
        attend_time_dic.update({sheets.id: attend_time_sum}) # 每个sheet总的attend time

    content_list = models.ControlTableContent.objects.filter(ControlTable_List_id=lid)
    new_list = []
    new_dic = {}

    # 将每个sheet所有SKU信息整合到同个字典中方便使用
    count = 0
    for i in content_list:
        count += 1

        new_dic.update({'sheet_id': i.sheet_id_id, 'sheet_name': i.sheet_id.sheet_name,'attend_time':attend_time_dic[i.sheet_id_id],
                        'sheet_description': i.sheet_id.sheet_description})
        new_dic.update({'sku' + str(count % int(plist['stage_sku_qty'])): i.tester})

        if count % int(plist['stage_sku_qty']) == 0:
            new_dic.update({'sku' + str(int(plist['stage_sku_qty'])): i.tester,'test_result':sheet_result_list[i.sheet_id.sheet_name]})

            # new_list.append(new_dic) # 字典更新会让list同步更新，需要将整个字典赋值
            new_list.append(dict(new_dic))

    # 检测result结果中该list中此case此sku有无结果
    done_reuslt_list={}
    sku_list=[]
    done_result_sku = models.TestResult.objects.filter(ControlTableList_id=lid).values('sku_num').distinct()
    for i in done_result_sku:
        sku_list.append(int(i['sku_num']))
    for k in sku_list:
        sh_list = []
        done_result_sheet = models.TestResult.objects.filter(ControlTableList_id=lid).values('sheet','sku_num').distinct()
        for i in done_result_sheet:
            if int(i['sku_num'])==k:
                sh_list.append(i['sheet'])
        done_reuslt_list[k]=sh_list

    return render(request, 'Project/task_table.html', {"pj": pj, "plist": plist,"SKU_Num_list": SKU_Num_list,"new_list": new_list,"done_reuslt_list":done_reuslt_list})


def task_list(request):
    CT_lists=[]
    CT = models.ControlTableContent.objects.filter(tester_id=request.user.id).values_list('ControlTable_List_id_id',flat=True).distinct()
    for i in CT:
        CT_list=models.ControlTableList.objects.filter(id=i).values().first()
        CT_lists.append(CT_list)
    for i in CT_lists:
        project = models.Project.objects.filter(id=i['project_id']).values().first()
        i['project']=project
    return render(request,'Project/task_list.html',{"CT_list":CT_lists})


def result_review(request,lid,sid,skunum):
    if request.method == 'GET':
        plist = models.ControlTableList.objects.filter(id=lid).values().first()
        pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
        name = T.Sheet.objects.filter(id=sid).values().first()['sheet_name']
        cases = T.TestCase.objects.filter(sheet_id=sid)
        result=models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=sid,sku_num=skunum,)

        result_list=[]

        for j in cases:
            result_dic = {'case_id': j.id, 'test_case_id': j.case_id, 'case_name': j.case_name,
                          'procedure': j.procedure, 'pass_criteria': j.pass_criteria, 'result': ''}

            for i in result:
                if i.test_case.id == j.id:
                    result_dic['result'] = i.test_result
                    result_dic['remark'] = i.remark
            result_list.append(result_dic)

        return render(request,'Project/result_review.html',{'result_list':result_list,"pj": pj, "plist": plist,"cases":cases,"skunum":skunum,"name":name})
    else:

        case_id_list = request.POST.getlist('case_id')
        result_list = request.POST.getlist('test_result')
        result = dict(zip(case_id_list, result_list))
        for i in result:
            if result[i] =="":
                continue
            else:
                if models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=i,sku_num=skunum):
                    models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=i,sku_num=skunum).update(test_result=result[i])
                else:
                    models.TestResult.objects.create(ControlTableList_id=lid, sku_num=skunum, test_case_id=int(i),
                                                     test_result=result[i], tester_id=request.user.id, sheet_id=sid)
        return redirect('task_table', lid=lid)