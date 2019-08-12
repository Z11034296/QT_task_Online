from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from Project.forms import *
from Project import models
import TestCase.models as T
import UserProfile.models as U
from collections import Counter
from itertools import chain
from django.contrib import messages
import re
import xlwt
from io import BytesIO
from django.contrib.auth.decorators import permission_required


def index(request):
    return render(request, 'Project/index.html')


# @permission_required('Tester')
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
    print(request.path_info)
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
        # pj = models.Project.objects.filter(id=plist["project_id"]).values().first()

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

    # 计算progress
    sheets_list = T.Sheet.objects.all()
    CT_list = models.ControlTableList.objects.filter(project_id=nid)
    pj = models.Project.objects.filter(id=nid).values().first()
    ct_list = models.ControlTableContent.objects.values("ControlTable_List_id_id").distinct()
    ct_list_distinct=[]
    progress={}
    att_time={}
    for i in ct_list:
        ct_list_distinct.append(i["ControlTable_List_id_id"])

        attend_time_dic = {}
        attend_time_dic_persheet = {}
        test_sku_num_list = {}
        for sheets in sheets_list:
            # *******计算非N/A的SKU的sku数量*********
            test_sku_num = 0
            x = models.ControlTableContent.objects.filter(sheet_id=sheets.id,ControlTable_List_id=i["ControlTable_List_id_id"])
            for j in x:
                if j.tester.name != "N/A":
                    test_sku_num += 1
            test_sku_num_list.update({sheets.id: test_sku_num})
            # 计算每个sheet的case attend time之和
            cases_by_sheet = T.TestCase.objects.filter(sheet_id=sheets.id).values('attend_time')
            attend_time_sum = 0
            for k in cases_by_sheet:
                attend_time_sum += int(k['attend_time'])
            attend_time_dic_persheet.update({sheets.id: attend_time_sum})
            attend_time_dic.update({sheets.id: attend_time_sum * int(test_sku_num_list[sheets.id])})
            att_time.update({i["ControlTable_List_id_id"]:sum(attend_time_dic.values())})
        y=models.TestResult.objects.filter(ControlTableList_id=i["ControlTable_List_id_id"]).values("test_case_id")
        attend_time_finished=0
        for k in y:
            attend_time_finished += int(T.TestCase.objects.filter(id=k["test_case_id"]).values("attend_time").first()["attend_time"])
        # progress.update({models.ControlTableList.objects.filter(id=i["ControlTable_List_id_id"]).values("project_stage").first()['project_stage']:'{:.2%}'.format(int(attend_time_finished)/sum(attend_time_dic.values()))})
        progress.update({i["ControlTable_List_id_id"]:'{:.2%}'.format(int(attend_time_finished)/sum(attend_time_dic.values()))})
    for i in CT_list:
        if i.id in progress.keys():
            i.attend_time=att_time[i.id]
            i.progressed = progress[i.id]
        else:
            i.attend_time="N/A"
            i.progressed="未开始"

    return render(request, 'Project/project_ct_info.html', {"CT_list":CT_list, "pj":pj,"ct_list_distinct":ct_list_distinct,"progress":progress})


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
        stage_sku = request.POST.get("stage_sku_qty")
        stage_note = request.POST.get("stage_note")
        if (int(project_id),project_stage) in result_list:
            error='该project已经有这个stage了'
            return render(request, 'Project/project_ct_list.html', {"pj":pj,'error':error})
        if result["stage_end"] and result["stage_begin"] != "":
            models.ControlTableList.objects.create(project_stage=result["project_stage"],project_id=result["project_id"],
                                                   stage_sku_qty=result["stage_sku_qty"],stage_note=result["stage_note"],stage_end=result["stage_end"],stage_begin=result["stage_begin"])
        elif result["stage_end"] == "":
            models.ControlTableList.objects.create(project_stage=result["project_stage"],
                                                   project_id=result["project_id"],
                                                   stage_sku_qty=result["stage_sku_qty"],
                                                   stage_note=result["stage_note"],
                                                   stage_begin=result["stage_begin"])
        elif result["stage_begin"] == "":
            models.ControlTableList.objects.create(project_stage=result["project_stage"],
                                                   project_id=result["project_id"],
                                                   stage_sku_qty=result["stage_sku_qty"],
                                                   stage_note=result["stage_note"],
                                                   stage_end=result["stage_end"])
        else:
            models.ControlTableList.objects.create(project_stage=result["project_stage"],
                                                   project_id=result["project_id"],
                                                   stage_sku_qty=result["stage_sku_qty"],
                                                   stage_note=result["stage_note"],
                                                   )
        return redirect('project_ct_info',nid)


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
    res_list = models.TestResult.objects.filter(ControlTableList_id=lid).values('sheet_id', 'test_result','remark')
    sheet_result_list = {}
    bugid_dic={}
    for i in sheets_list:
        re_list = []
        bugid_list=[]
        final_result = ''
        for j in res_list:
            if i.id == int(j['sheet_id']):
                if 'refer to bug ' in j['remark']:
                    bugid_list.append(int(re.findall(r"\d+",j['remark'])[0])) # 取 bug ID
                    bugid_list = list(set(bugid_list)) # 列表去重
                    bugid_list.sort(reverse = False) # 排序
                re_list.append(j['test_result'])
                if 'Fail' in re_list:
                    final_result = 'Fail'
                elif re_list == []:
                    final_result = ''
                else:
                    final_result = 'Pass'
        bugid_dic[i.id] = bugid_list
        sheet_result_list[i.sheet_name] = final_result
    # 每个sheet中的case个数填入sheets_list
    attend_time_dic={}
    attend_time_dic_persheet={}
    test_sku_num_list={}
    for sheets in sheets_list:
        sheets.count = cout[sheets.sheet_name]
        # *******计算非N/A的SKU的sku数量*********
        test_sku_num=0
        x=models.ControlTableContent.objects.filter(ControlTable_List_id=lid,sheet_id=sheets.id)
        for j in x:
            if j.tester.name != "N/A":
                test_sku_num += 1
        test_sku_num_list.update({sheets.id:test_sku_num})
        # 计算每个sheet的case attend time之和
        cases_by_sheet = T.TestCase.objects.filter(sheet_id=sheets.id).values('attend_time')
        attend_time_sum = 0
        for i in cases_by_sheet:
            attend_time_sum += int(i['attend_time'])
        attend_time_dic_persheet.update({sheets.id: attend_time_sum})
        attend_time_dic.update({sheets.id: attend_time_sum * int(test_sku_num_list[sheets.id])})

    # progress_sheet=models.TestResult.objects.filter(ControlTableList_id=lid).values("sheet_id").distinct()
    # for i in progress_sheet:
    #     result_case_time=models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i['sheet_id'])
    #     for j in result_case_time:

    content_list = models.ControlTableContent.objects.filter(ControlTable_List_id=lid)
    new_list = []
    new_dic = {}
    # 将每个sheet所有SKU信息整合到同个字典中方便使用
    count=0
    for i in content_list:
        # 计算test result的progress
        time_result = models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i.sheet_id_id)
        finished_attend_time_dic = {"sku0":0}
        for k in SKU_Num_list:
            finished_attend_time = 0
            for j in time_result:
                if int(k) == int(j.sku_num):
                    finished_attend_time += int(j.test_case.attend_time)
            if attend_time_dic[i.sheet_id_id] != 0:
                finished_attend_time_dic.update({"sku"+str(k):'{:.0%}'.format(finished_attend_time / attend_time_dic_persheet[i.sheet_id_id]) })
            else:
                finished_attend_time_dic.update({"sku" + str(k): '0%' })
        # ******************************************************************************************
        count+=1
        new_dic.update({'sheet_id':i.sheet_id_id,'sheet_name':i.sheet_id.sheet_name,'attend_time':attend_time_dic[i.sheet_id_id],
                        'sheet_description':i.sheet_id.sheet_description,"bugid":bugid_dic[i.sheet_id_id]})
        new_dic.update({'sku'+str(count % int(plist['stage_sku_qty'])):i.tester,'sku'+str(count % int(plist['stage_sku_qty']))+'_progress':finished_attend_time_dic['sku'+str(count % int(plist['stage_sku_qty']))]})

        if count % int(plist['stage_sku_qty']) == 0:
            new_dic.update({'sku' + str(int(plist['stage_sku_qty'])): i.tester,'test_result':sheet_result_list[i.sheet_id.sheet_name],'sku'+plist['stage_sku_qty']+'_progress':finished_attend_time_dic['sku'+plist['stage_sku_qty']]})

            # new_list.append(new_dic) # 字典更新会让list同步更新，需要将整个字典赋值
            new_list.append(dict(new_dic))
    return render(request, 'Project/project_ct_content.html', {"pj": pj, "plist": plist,
                                                               "SKU_Num_list": SKU_Num_list,"new_list":new_list})


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
            if result[i] != "":
                models.TestResult.objects.create(ControlTableList_id=lid,sku_num=skunum,test_case_id=int(i),
                                                 test_result=result[i],tester_id=request.user.id,sheet_id=sid,
                                                 remark=remark_result[i],result_info_id = result_info_id['id'])
            else:
                pass
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
        # attend_time_dic.update({sheets.id: attend_time_sum}) # 每个sheet总的attend time

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
                    if "refer to bug " in i.remark:
                        result_dic['bug_id'] = int(re.findall(r"\d+",i.remark)[0])
                    # else:result_dic['bug_id'] = ''
            result_list.append(result_dic)
        return render(request,'Project/result_review.html',{'result_list':result_list,"pj": pj, "plist": plist,"cases":cases,"skunum":skunum,"name":name,'sid':sid})
    else:
        project = models.Project.objects.filter(id=lid).values('id').first()
        result_info_id = models.ProjectInfo.objects.filter(project_id=project['id']).values("id").last()
        case_id_list = request.POST.getlist('case_id')
        result_list = request.POST.getlist('test_result')
        result = dict(zip(case_id_list, result_list))
        remark_list = request.POST.getlist('remark')
        result_remark = dict(zip(case_id_list, remark_list))
        for i in result:
            if result[i] =="":
                continue
            else:
                if models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=i,sku_num=skunum):
                    models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=i,sku_num=skunum).update(test_result=result[i],result_info_id=result_info_id['id'],tester_id=request.user.id,)
                    if result[i] == 'Pass' and "refer to bug " in result_remark[i]:
                        models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                         sku_num=skunum).update(remark='')
                else:
                    models.TestResult.objects.create(ControlTableList_id=lid, sku_num=skunum, test_case_id=int(i),
                                                     test_result=result[i], tester_id=request.user.id, sheet_id=sid,result_info_id=result_info_id['id'])
        return redirect("task_table",lid=lid)


def result_check(request,lid,sid,skunum):
    if request.method == 'GET':
        plist = models.ControlTableList.objects.filter(id=lid).values().first()
        pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
        name = T.Sheet.objects.filter(id=sid).values().first()['sheet_name']
        cases = T.TestCase.objects.filter(sheet_id=sid)
        result = models.TestResult.objects.filter(ControlTableList_id=lid, sheet_id=sid, sku_num=skunum, )
        result_list = []
        for j in cases:
            result_dic = {'case_id': j.id, 'test_case_id': j.case_id, 'case_name': j.case_name,
                          'procedure': j.procedure, 'pass_criteria': j.pass_criteria, 'result': ''}
            for i in result:
                if i.test_case.id == j.id:
                    result_dic['result'] = i.test_result
                    result_dic['remark'] = i.remark
                    if "refer to bug " in i.remark:
                        result_dic['bug_id'] = int(re.findall(r"\d+", i.remark)[0])
                    # else:result_dic['bug_id'] = ''
            result_list.append(result_dic)
        return render(request, 'Project/result_review.html',
                      {'result_list': result_list, "pj": pj, "plist": plist, "cases": cases, "skunum": skunum,
                       "name": name, 'sid': sid})
    else:
        plist = models.ControlTableList.objects.filter(id=lid).values().first()
        project = models.Project.objects.filter(id=plist["project_id"]).values('id').first()
        result_info_id = models.ProjectInfo.objects.filter(project_id=project['id']).values("id").last()
        case_id_list = request.POST.getlist('case_id')
        result_list = request.POST.getlist('test_result')
        result = dict(zip(case_id_list, result_list))
        remark_list = request.POST.getlist('remark')
        result_remark = dict(zip(case_id_list, remark_list))
        for i in result:
            if result[i] =="":
                continue
            else:
                if models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i, sku_num=skunum):
                    models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i, sku_num=skunum).update(
                        test_result=result[i], result_info_id=result_info_id['id'], tester_id=request.user.id, )
                    if result[i] == 'Pass' and "refer to bug " in result_remark[i]:
                        models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                         sku_num=skunum).update(remark='')
                else:
                    models.TestResult.objects.create(ControlTableList_id=lid, sku_num=skunum, test_case_id=int(i),
                                                     test_result=result[i], tester_id=request.user.id, sheet_id=sid,
                                                     result_info_id=result_info_id['id'])
        return redirect("project_ct_content",lid=lid)


def stage_update(request,lid):
    if request.method == "GET":
        plist = models.ControlTableList.objects.filter(id=lid).values().first()
        pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
        info = models.ControlTableList.objects.filter(id=lid).values().first()
        return render(request,'Project/stage_update.html',{'info':info,'pj':pj})
    else:
        models.ControlTableList.objects.filter(id=lid).update(project_stage=request.POST.get("project_stage"),stage_sku_qty=request.POST.get("stage_sku_qty"),stage_begin=request.POST.get("stage_begin"),stage_end=request.POST.get("stage_end"),stage_note=request.POST.get("stage_note"),)
        # plist = models.ControlTableList.objects.filter(id=lid).values().first()
        # pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
        CT_list = models.ControlTableList.objects.filter(project_id=request.POST.get("project_id"))
        pj = models.Project.objects.filter(id=request.POST.get("project_id")).values().first()
        ct_list = models.ControlTableContent.objects.values("ControlTable_List_id_id").distinct()
        ct_list_distinct = []
        for i in ct_list:
            ct_list_distinct.append(i["ControlTable_List_id_id"])

        return render(request, 'Project/project_ct_info.html',
                      {"CT_list": CT_list, "pj": pj, "ct_list_distinct": ct_list_distinct})


def issue_list(request,pid):
    pj = models.Project.objects.filter(id=pid).values().first()
    issue_list=models.Issue.objects.filter(project_id=pid)
    return render(request,'Project/issue_list.html',{"pj":pj,"issue_list":issue_list})


def refer_issue(request,pid,iss_id):
    pj = models.Project.objects.filter(id=pid).values().first()
    issue = models.Issue.objects.filter(project_id=pid,issue_id=iss_id)
    return render(request,'Project/issue_list.html',{"pj":pj,"issue_list":issue})


def add_issue(request,pid):
    if request.method == "GET":
        pj = models.Project.objects.filter(id=pid).values().first()
        return render(request, 'Project/add_issue.html', {"pj": pj})
    else:
        if models.Issue.objects.filter(project_id=pid):
            issue=models.Issue.objects.filter(project_id=pid).values().last()
            issue_id=issue["issue_id"]+1
        else:
            issue_id = 1

        controltablelist_id=models.ControlTableList.objects.filter(project_id=pid).values().last()
        models.Issue.objects.create(
            project_id=pid,
            ControlTableList_id=controltablelist_id["id"],
            submitter_id=request.user.id,
            issue_id=issue_id,
            bugzilla_id=request.POST.get("bugzilla_id"),
            TRID=request.POST.get("TRID"),
            category=request.POST.get("category"),
            attribute=request.POST.get("attribute"),
            attribute_name=request.POST.get("attribute_name"),
            severity=request.POST.get("severity"),
            description=request.POST.get("description"),
            procedure=request.POST.get("procedure"),
            comment=request.POST.get("comment"),
            root_cause="",
            solution="",
            status=request.POST.get("status"),
            # solving_type=request.POST.get("solving_type"),
            open_date=request.POST.get("open_date"),
            # verify_date=request.POST.get("verify_date"),
            # close_date=request.POST.get("close_date"),
            owner=request.POST.get("owner"),
            motherboard_version=request.POST.get("motherboard_version"),
            bios_version=request.POST.get("bios_version"),
            os_version=request.POST.get("os_version"),
            remark=request.POST.get("remark"),
        )
        pj = models.Project.objects.filter(id=pid).values().first()
        issue_list = models.Issue.objects.filter(project_id=pid)
        return render(request,"Project/issue_list.html",{"pj":pj,"issue_list":issue_list})


def issue_update(request,pid,bid):  # bid:issue表中的id
    if request.method == "GET":
        pj = models.Project.objects.filter(id=pid).values().first()
        issue=models.Issue.objects.filter(project_id=pid,id=bid).values().first()
        return render(request,"Project/issue_update.html",{"pj":pj,"issue":issue})
    else:

        models.Issue.objects.filter(project_id=pid, id=bid).update(
            bugzilla_id=request.POST.get("bugzilla_id"),
            TRID=request.POST.get("TRID"),
            category=request.POST.get("category"),
            attribute=request.POST.get("attribute"),
            attribute_name=request.POST.get("attribute_name"),
            severity=request.POST.get("severity"),
            description=request.POST.get("description"),
            procedure=request.POST.get("procedure"),
            comment=request.POST.get("comment"),
            root_cause=request.POST.get("root_cause"),
            solution=request.POST.get("solution"),
            status=request.POST.get("status"),
            solving_type=request.POST.get("solving_type"),
            open_date=request.POST.get("open_date"),
            # verify_date=request.POST.get("verify_date"),
            # close_date=request.POST.get("close_date"),
            owner=request.POST.get("owner"),
            motherboard_version=request.POST.get("motherboard_version"),
            bios_version=request.POST.get("bios_version"),
            os_version=request.POST.get("os_version"),
            remark=request.POST.get("remark"),
        )
        if request.POST.get("verify_date") != "":
            models.Issue.objects.filter(project_id=pid, id=bid).update(
                verify_date=request.POST.get("verify_date"),
            )
        if request.POST.get("close_date") != "":
            models.Issue.objects.filter(project_id=pid, id=bid).update(
                close_date=request.POST.get("close_date"),
            )
        pj = models.Project.objects.filter(id=pid).values().first()
        issue_list = models.Issue.objects.filter(project_id=pid)
        return render(request, "Project/issue_list.html", {"pj": pj, "issue_list": issue_list})


def change_tester(request,lid,sid,skunum):
    if request.method == "GET":
        test_user = U.UserInfo.objects.filter(site_id="1")
        return render(request,"Project/change_tester.html",{"test_user":test_user,"lid":lid,"sid":sid,"skunum":skunum})
    else:
        models.ControlTableContent.objects.filter(ControlTable_List_id_id=lid,sheet_id_id=sid,sku_num=skunum).update(
            tester=request.POST.get("changed_tester")
        )
        return redirect("project_ct_content",lid)


def asign_bug(request,pid,lid,cid,sid,skunum):
    if request.method == "GET":
        return render(request, 'Project/asign_bug.html',{"pid":pid,"lid":lid,"cid":cid,"sid":sid,"skunum":skunum})
    else:
        if request.POST.get("asign_bug"):
            bug=models.Issue.objects.filter(project_id=pid,issue_id=int(request.POST.get("asign_bug"))).values().first()
            if bug:
                models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=cid,sku_num=skunum).update(remark="refer to bug "+request.POST.get("asign_bug")+":"+bug["description"])
            else:messages.success(request, "输入错误")
            return redirect("result_review",lid,sid,skunum)
        else:
            messages.success(request, "输入错误")
            return redirect("result_review",lid,sid,skunum)


def export_project_report(self, lid):
    sheets_list = T.Sheet.objects.all()
    sku_n = models.ControlTableList.objects.filter(id=lid).values().first()['stage_sku_qty']
    if sheets_list:
        ws=xlwt.Workbook(encoding='utf8')

        style_heading = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index black,
                bold on,
                height 0x014A;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour orange ;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

        style_heading_2 = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index black,
                bold on,
                height 0xC8;
            align:
                wrap on,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour orange ;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

        style_body_1 = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index black,
                bold off,
                height 0xC8;
            align:
                wrap on,
                vert center,
                horiz center;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

        style_body_2 = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index black,
                bold off,
                height 0xC8;
            align:
                wrap on,
                vert center,
                horiz left;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

        style_result_pass = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index blue,
                bold off,
                height 0xC8;
            align:
                wrap on,
                vert center,
                horiz center;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
        style_result_fail = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index red,
                bold off,
                height 0xC8;
            align:
                wrap on,
                vert center,
                horiz center;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
        style_back = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index blue,
                bold on,
                height 0xC8;
            align:
                wrap on,
                vert center,
                horiz center;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            pattern:
                pattern solid,
                fore-colour orange ;    
            """)
        # ***********************************************
        # ***********************************************
        # 生成table of Contents
        project_stage=models.ControlTableList.objects.filter(id=lid).values().first()['project_stage']
        project_id=models.ControlTableList.objects.filter(id=lid).values().first()['project_id']
        project=models.Project.objects.filter(id=project_id).values().first()
        w_c = ws.add_sheet('Table_of_Contents',cell_overwrite_ok=True)

        # w.write(2, 2, project['project_name']+' '+project['project_model']+' '+project_stage+' Compatibility Test Report')
        # w.write(3, 1, 'Project:'+' '+project['project_name']+' '+project['project_model'])
        w_c.write_merge(4, 5, 0, 0, 'Item No.',style_heading_2)
        w_c.write_merge(4, 5, 1, 1, 'Description',style_heading_2)
        w_c.write_merge(4, 5, 2, 2, 'Total Sub-item',style_heading_2)
        w_c.write_merge(4, 5, 3, 3, 'Note',style_heading_2)
        w_c.write_merge(4, 5, 4, 4, 'Result',style_heading_2)
        k = 0
        while k < int(sku_n):
            # w.write(2, 4 + k, '')
            w_c.write_merge(4, 4, 5, 5+k, 'Test SKU',style_heading_2)
            w_c.write(5, 5 + k, 'SKU'+str(k+1),style_heading_2)
            w_c.col(5+k).width = 1500
            k += 1
        w_c.write_merge(4, 5, 5 + int(sku_n),5 + int(sku_n), 'Remark',style_heading_2)

        w_c.col(0).width = 2700
        w_c.col(1).width = 15000
        w_c.col(2).width = 2500
        w_c.col(3).width = 2500
        w_c.col(4).width = 2500
        w_c.col(5 + int(sku_n)).width = 13000
        w_c.write_merge(0, 1, 0, 4,project['project_name']+' '+project['project_model']+' '+project_stage+' Compatibility Test Report',style_heading)
        w_c.write_merge(2, 3, 0, 4,'Project:'+' '+project['project_name']+' '+project['project_model'],style_heading)
        # w.write_merge(2, 3, 0, 0,'',style_title1)
        w_c.write_merge(0, 1, 5, 5 + int(sku_n),'',style_heading)
        w_c.write_merge(2, 3, 5, 5 + int(sku_n),'',style_heading)
        excel_row_C = 6


        # 对每个sheet进行生成
        for i in sheets_list:
            w = ws.add_sheet(i.sheet_name,cell_overwrite_ok=True)

            # w.write(2, 0, 'Case_id',style_heading_2)
            w.write(2, 0, 'Case_name',style_heading_2)
            w.write(2, 1, 'Procedure',style_heading_2)
            w.write(2, 2, 'Pass_critearia',style_heading_2)
            k = 0
            while k<int(sku_n):
                w.write(0, 0,xlwt.Formula('HYPERLINK("#Table_of_Contents!A1","Go Back")'),style_back)
                w.write_merge(0, 0, 1, 4 + k, 'Test Suite:' + i.sheet_name,style_heading_2)
                w.write(1, 0, "",style_heading_2)
                w.write_merge(1, 1, 1, 4 + k, i.sheet_description,style_heading_2)
                w.write(2, 3+k, 'SKU'+str(k+1),style_heading_2)
                w.col(4 + k).width = 1500
                k+=1
            # w.write(2, 4, 'SKU1')
            w.write(2, 3+int(sku_n), 'Notes/Comment',style_heading_2)

            w.col(0).width = 4500
            # w.col(1).width = 4500
            w.col(1).width = 15000
            w.col(2).width = 15000
            w.col(3 + int(sku_n)).width = 13000
            excel_row = 3

            # result_list=models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i.id).values()
            li=models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i.id).values_list('test_case_id').distinct()
            for x in li:
            # for j in result_list:
            #     case_id=T.TestCase.objects.filter(id=x[0]).values().first()['case_id']
                case_name=T.TestCase.objects.filter(id=x[0]).values().first()['case_name']
                procedure=T.TestCase.objects.filter(id=x[0]).values().first()['procedure']
                pass_criteria=T.TestCase.objects.filter(id=x[0]).values().first()['pass_criteria']
                # Notes_Comment=T.TestCase.objects.filter(id=x[0]).values().first()['remark']
                # 写入数据

                # w.write(excel_row, 0, case_id,style_body_2)
                w.write(excel_row, 0, case_name,style_body_2)
                w.write(excel_row, 1, procedure,style_body_2)
                w.write(excel_row, 2, pass_criteria,style_body_2)
                # for l in  SKU_N_list:
                l = 1
                while l <= int(sku_n):
                    try:
                        result=models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i.id,sku_num=str(l),test_case_id=x[0]).values().first()['test_result']
                    except :
                        result=''
                    if result == "Pass":
                        w.write(excel_row, 2+l, result, style_result_pass)
                    elif result == "Fail":
                        w.write(excel_row, 2+l, result, style_result_fail)
                    else:
                        w.write(excel_row, 2+l, result, style_body_1)
                    # w.write(excel_row, 3+l, result,style_body_1)
                    l += 1
                #****************************************************
                # Note/Comment 无法追写到同一个单元格内，需要重新计算
                Notes_Comment=models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i.id,test_case_id=x[0]).values('remark')
                notes = ''
                for y in Notes_Comment:
                    if y['remark']!='':
                        if notes=='':
                            notes=y['remark']
                        else:
                            notes=notes+';'+ y['remark']
                w.write(excel_row, 3+int(sku_n), notes,style_body_2)

                # w.write(excel_row, 5, Notes_Comment)
                excel_row += 1
                # *************************************************
        # 后写Table of Contents
        # *********************Table of Contents内容********************************
        plist = models.ControlTableList.objects.filter(id=lid).values().first()
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
        res_list = models.TestResult.objects.filter(ControlTableList_id=lid).values('sheet_id', 'test_result',
                                                                                    'remark')
        sheet_result_list = {}
        bugid_dic = {}
        for i in sheets_list:
            re_list = []
            bugid_list = []
            final_result = ''
            for j in res_list:
                if i.id == int(j['sheet_id']):
                    if 'refer to bug ' in j['remark']:
                        bugid_list.append(int(re.findall(r"\d+", j['remark'])[0]))  # 取 bug ID
                        bugid_list = list(set(bugid_list))  # 列表去重
                        bugid_list.sort(reverse=False)  # 排序
                    re_list.append(j['test_result'])
                    if 'Fail' in re_list:
                        final_result = 'Fail'
                    elif re_list == []:
                        final_result = ''
                    else:
                        final_result = 'Pass'
            bugid_dic[i.id] = bugid_list
            sheet_result_list[i.sheet_name] = final_result
        # 每个sheet中的case个数填入sheets_list
        attend_time_dic = {}
        attend_time_dic_persheet = {}
        test_sku_num_list = {}
        for sheets in sheets_list:
            sheets.count = cout[sheets.sheet_name]
            # *******计算非N/A的SKU的sku数量*********
            test_sku_num = 0
            x = models.ControlTableContent.objects.filter(ControlTable_List_id=lid, sheet_id=sheets.id)
            for j in x:
                if j.tester.name != "N/A":
                    test_sku_num += 1
            test_sku_num_list.update({sheets.id: test_sku_num})
            # 计算每个sheet的case attend time之和
            cases_by_sheet = T.TestCase.objects.filter(sheet_id=sheets.id).values('attend_time')
            attend_time_sum = 0
            for i in cases_by_sheet:
                attend_time_sum += int(i['attend_time'])
            attend_time_dic_persheet.update({sheets.id: attend_time_sum})
            attend_time_dic.update({sheets.id: attend_time_sum * int(test_sku_num_list[sheets.id])})
        content_list = models.ControlTableContent.objects.filter(ControlTable_List_id=lid)
        new_list = []
        new_dic = {}
        # 将每个sheet所有SKU信息整合到同个字典中方便使用
        count = 0
        for i in content_list:
            # 计算test result的progress
            time_result = models.TestResult.objects.filter(ControlTableList_id=lid, sheet_id=i.sheet_id_id)
            finished_attend_time_dic = {"sku0": 0}
            for k in SKU_Num_list:
                finished_attend_time = 0
                for j in time_result:
                    if int(k) == int(j.sku_num):
                        finished_attend_time += int(j.test_case.attend_time)
                if attend_time_dic[i.sheet_id_id] != 0:
                    finished_attend_time_dic.update({"sku" + str(k): '{:.0%}'.format(
                        finished_attend_time / attend_time_dic_persheet[i.sheet_id_id])})
                else:
                    finished_attend_time_dic.update({"sku" + str(k): '0%'})
            # ******************************************************************************************
            count += 1
            new_dic.update({'sheet_id': i.sheet_id_id, 'sheet_name': i.sheet_id.sheet_name,
                            'attend_time': attend_time_dic[i.sheet_id_id],
                            'sheet_description': i.sheet_id.sheet_description, "bugid": bugid_dic[i.sheet_id_id]})
            new_dic.update({'sku' + str(count % int(plist['stage_sku_qty'])): i.tester,
                            'sku' + str(count % int(plist['stage_sku_qty'])) + '_progress':
                                finished_attend_time_dic[
                                    'sku' + str(count % int(plist['stage_sku_qty']))]})

            if count % int(plist['stage_sku_qty']) == 0:
                new_dic.update({'sku' + str(int(plist['stage_sku_qty'])): i.tester,
                                'test_result': sheet_result_list[i.sheet_id.sheet_name],
                                'sku' + plist['stage_sku_qty'] + '_progress': finished_attend_time_dic[
                                    'sku' + plist['stage_sku_qty']]})

                # new_list.append(new_dic) # 字典更新会让list同步更新，需要将整个字典赋值
                new_list.append(dict(new_dic))

        # *********************************************************

        for i in new_list:
            w_c.write(excel_row_C, 0,
                      xlwt.Formula('HYPERLINK("#' + i['sheet_name'] + '!B1",' + '"' + i["sheet_name"] + '")'), style_body_1)
            # "i['sheet_name'], style_body_1)
            w_c.write(excel_row_C, 1, xlwt.Formula('HYPERLINK("#' + i['sheet_name'] + '!B1",' + '"' + i['sheet_description'] + '")'), style_body_2)
            w_c.write(excel_row_C, 2, cout[i['sheet_name']], style_body_1)
            w_c.write(excel_row_C, 3, '', style_body_2)
            if i['test_result'] == "Pass":
                w_c.write(excel_row_C, 4, i['test_result'], style_result_pass)
            elif i['test_result'] == "Fail":
                w_c.write(excel_row_C, 4, i['test_result'], style_result_fail)
            else:
                w_c.write(excel_row_C, 4, i['test_result'], style_body_1)
            k = 0
            while k < int(sku_n):
                # w.write(2, 4 + k, '')
                if i['sku' + str(k + 1) + '_progress'] == '100%':
                    w_c.write(excel_row_C, 5 + k, i['sku' + str(k + 1) + '_progress'], style_result_pass)
                else:
                    w_c.write(excel_row_C, 5 + k, i['sku' + str(k + 1) + '_progress'], style_body_1)
                k += 1
            if i['bugid'] != []:
                w_c.write(excel_row_C, 5 + int(sku_n), 'refer to bugID: ' + str(i['bugid']), style_body_2)
            else:
                w_c.write(excel_row_C, 5 + int(sku_n), '', style_body_1)
            excel_row_C += 1

        # 写出到IO
        sio = BytesIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=report.xls'
        response.write(sio.getvalue())
        return response
        # return HttpResponse('OKOKOKOKOK')