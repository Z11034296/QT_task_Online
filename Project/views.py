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
import xlrd,xlwt,xlsxwriter
import datetime
from io import BytesIO
from django.contrib.auth.decorators import permission_required


def index(request):
    return render(request, 'Project/index.html')


# @permission_required('Tester')
def projects(request):

    result = models.Project.objects.all().order_by('-schedule_end')
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
            # 所选择的member设为 TL权限
            if U.UserInfo.objects.get(id=obj.cleaned_data['test_leader_wzs_id']).role.values().first()['id'] not in [4,5]:
                U.UserInfo.objects.get(id=obj.cleaned_data['test_leader_wzs_id']).role.set('3')
            return redirect('add_project_info',p.project_id)
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
        # pro_id=models.ControlTableList.objects.filter(id=nid).values().first()['project_id']
        ret = models.ProjectInfo.objects.filter(project_id=nid).values().last()
        ret['project_name']=models.Project.objects.filter(id=nid).values().first()['project_name']
        return render(request, 'Project/project_info.html', {'nid': nid, 'ret': ret})


def add_project_info(request, nid):

    if request.method == "GET":
        pj = models.Project.objects.filter(project_id=nid).values().first()
        return render(request, 'Project/add_project_info.html', {'pj': pj})
    else:
        pj = models.Project.objects.filter(project_id=nid).values().first()
        models.ProjectInfo.objects.create(
            project_id=request.POST.get('project_id'),
            project_bios=request.POST.get('BIOS_ver'),
            project_mb=request.POST.get('MB_ver'),
            project_os=request.POST.get('OS'),
            dr_chipset=request.POST.get('chipset'),
            dr_vga=request.POST.get('VGA'),
            dr_iamt=request.POST.get('IAMT'),
            dr_storage=request.POST.get('Storage'),
            dr_lan=request.POST.get('LAN'),
            dr_audio=request.POST.get('audio'),
            dr_wireless=request.POST.get('Wireless'),
            dr_bt=request.POST.get('Bluetooth'),
            dr_panel=request.POST.get('Panel'),
            dr_finger_printer=request.POST.get('Finger_printer'),
            dr_g_sensor=request.POST.get('G_sensor'),
            dr_camera=request.POST.get('Camera'),
            dr_usb=request.POST.get('USB'),
            dr_com_parallel=request.POST.get('Com_parallel'),
            dr_serial_io=request.POST.get('Serial_io'),
            dr_sgx=request.POST.get('SGX'),
            dr_others=request.POST.get('Others'),
            dr_cr=request.POST.get('Cardreader'),

        )
        return redirect('projects')


def edit_project_info(request, nid):
    if request.method == "GET":
        ret = models.ProjectInfo.objects.filter(id=nid).values().last()

        ret['project_name'] = models.Project.objects.filter(id=ret['project_id']).values().first()['project_name']
        return render(request, 'Project/edit_project_info.html', {'ret': ret})
    else:
        models.ProjectInfo.objects.create(
            project_id=request.POST.get('project_id'),
            project_bios=request.POST.get('BIOS_ver'),
            project_mb=request.POST.get('MB_ver'),
            project_os=request.POST.get('OS'),
            dr_chipset=request.POST.get('chipset'),
            dr_vga=request.POST.get('VGA'),
            dr_iamt=request.POST.get('IAMT'),
            dr_storage=request.POST.get('Storage'),
            dr_lan=request.POST.get('LAN'),
            dr_audio=request.POST.get('audio'),
            dr_wireless=request.POST.get('Wireless'),
            dr_bt=request.POST.get('Bluetooth'),
            dr_panel=request.POST.get('Panel'),
            dr_finger_printer=request.POST.get('Finger_printer'),
            dr_g_sensor=request.POST.get('G_sensor'),
            dr_camera=request.POST.get('Camera'),
            dr_usb=request.POST.get('USB'),
            dr_com_parallel=request.POST.get('Com_parallel'),
            dr_serial_io=request.POST.get('Serial_io'),
            dr_sgx=request.POST.get('SGX'),
            dr_others=request.POST.get('Others'),
            dr_cr=request.POST.get('Cardreader'),

        )
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
        test_user = U.UserInfo.objects.all().order_by('job_name')
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
        # add_list=[]
        for sheets in sheets_list:
            for i in SKU_Num_list:
                name = '{}-SKU{}'.format(sheets.id, i)
                tester=U.UserInfo.objects.filter(id=request.POST.get(name)).values().first()
                models.ControlTableContent.objects.create(sku_num=i,ControlTable_List_id_id=lid,
                                                          sheet_id_id=sheets.id,tester_id=tester["id"])
        return redirect('projects')


def project_ct_info(request,nid):

    # 计算progress
    # sheets_list = T.Sheet.objects.all()
    CT_list = models.ControlTableList.objects.filter(project_id=nid)
    pj = models.Project.objects.filter(id=nid).values().first()
    ct_list = models.ControlTableContent.objects.values("ControlTable_List_id_id").distinct()
    ct_list_distinct=[]
    # progress={}
    # att_time={}
    for i in ct_list:
        ct_list_distinct.append(i["ControlTable_List_id_id"])
    for i in CT_list:
        if i.attend_time == "N/A" or i.attend_time == "0":
            i.progressed = "0%"
        else:i.progressed= '{:.2%}'.format(float(i.finished_time) / float(i.attend_time))
    return render(request, 'Project/project_ct_info.html', {"CT_list":CT_list, "pj":pj,"ct_list_distinct":ct_list_distinct})


def update_attendtime(request,nid):
    # 计算progress
    sheets_list = T.Sheet.objects.all()
    CT_list = models.ControlTableList.objects.filter(project_id=nid)
    pj = models.Project.objects.filter(id=nid).values().first()
    ct_list = models.ControlTableContent.objects.values("ControlTable_List_id_id").distinct()
    li=[]
    for i in list(CT_list.values("id")):
        li.append(i["id"])
    ct_list_distinct = []
    progress = {}
    att_time = {}
    for i in ct_list:
        ct_list_distinct.append(i["ControlTable_List_id_id"])
        if i["ControlTable_List_id_id"] in li:
            attend_time_dic = {}
            test_sku_num_list = {}
            for sheets in sheets_list:
                # *******计算非N/A的SKU的sku数量*********
                test_sku_num = 0
                x = models.ControlTableContent.objects.filter(sheet_id=sheets.id,
                                                              ControlTable_List_id=i["ControlTable_List_id_id"])
                for j in x:
                    if j.tester.job_name != "N/A":
                        test_sku_num += 1
                test_sku_num_list.update({sheets.id: test_sku_num})
                attend_time_dic.update({sheets.id: float(
                    T.Sheet.objects.filter(id=sheets.id).values().first()["attend_time"]) * int(
                    test_sku_num_list[sheets.id])})
                att_time.update({i["ControlTable_List_id_id"]: sum(attend_time_dic.values())})
            y = models.TestResult.objects.filter(ControlTableList_id=i["ControlTable_List_id_id"]).values("test_case_id")
            attend_time_finished = 0
            for k in y:
                attend_time_finished += float(
                    T.TestCase.objects.filter(id=k["test_case_id"]).values("attend_time").first()["attend_time"])
            models.ControlTableList.objects.filter(id=i["ControlTable_List_id_id"]).update(finished_time=str(attend_time_finished),
                                                                                           attend_time=sum(attend_time_dic.values()))

        # progress.update({i["ControlTable_List_id_id"]: '{:.2%}'.format(
        #     float(attend_time_finished) / sum(attend_time_dic.values()))})
    for i in CT_list:
        if i.attend_time == "N/A" or i.attend_time == "0":
            i.progressed = "N/A"
        else:i.progressed= '{:.2%}'.format(float(i.finished_time) / float(i.attend_time))
    return render(request, 'Project/project_ct_info.html',
                  {"CT_list": CT_list, "pj": pj, "ct_list_distinct": ct_list_distinct})


def update_attendtime_all(request):
    # Manager用来更新所有project的attend time和Progress
    sheets_list = T.Sheet.objects.all()
    ct_list = models.ControlTableContent.objects.values("ControlTable_List_id_id").distinct()
    att_time = {}
    for i in ct_list:
        attend_time_dic = {}
        test_sku_num_list = {}
        for sheets in sheets_list:
            # *******计算非N/A的SKU的sku数量*********
            test_sku_num = 0
            x = models.ControlTableContent.objects.filter(sheet_id=sheets.id,
                                                              ControlTable_List_id=i["ControlTable_List_id_id"])
            for j in x:
                if j.tester.job_name != "N/A":
                    test_sku_num += 1
            test_sku_num_list.update({sheets.id: test_sku_num})
            attend_time_dic.update({sheets.id: float(
                T.Sheet.objects.filter(id=sheets.id).values().first()["attend_time"]) * int(
                test_sku_num_list[sheets.id])})
            att_time.update({i["ControlTable_List_id_id"]: sum(attend_time_dic.values())})
        y = models.TestResult.objects.filter(ControlTableList_id=i["ControlTable_List_id_id"]).values("test_case_id")
        attend_time_finished = 0
        for k in y:
            attend_time_finished += float(
                T.TestCase.objects.filter(id=k["test_case_id"]).values("attend_time").first()["attend_time"])
        models.ControlTableList.objects.filter(id=i["ControlTable_List_id_id"]).update(finished_time=str(attend_time_finished),
                                                                                           attend_time=sum(attend_time_dic.values()))
    return redirect("project_sum")


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
        if project_stage == "":
            project_stage="blank,please modify this item"
        stage_sku = request.POST.get("stage_sku_qty")
        stage_note = request.POST.get("stage_note")
        if (int(project_id),project_stage) in result_list:
            error='该project已经有这个stage了'
            return render(request, 'Project/project_ct_list.html', {"pj":pj,'error':error})
        if result["stage_end"] and result["stage_begin"] != "":
            models.ControlTableList.objects.create(project_stage=project_stage,
                                                   project_id=result["project_id"],
                                                   stage_sku_qty=result["stage_sku_qty"],
                                                   stage_note=result["stage_note"],
                                                   system_qty=result["system_qty"],
                                                   OS_Ver=result["OS_Ver"],
                                                   buffer_activity=result["buffer"],
                                                   stage_end=result["stage_end"],
                                                   stage_begin=result["stage_begin"])
        elif result["stage_end"] == "":
            models.ControlTableList.objects.create(project_stage=result["project_stage"],
                                                   project_id=result["project_id"],
                                                   stage_sku_qty=result["stage_sku_qty"],
                                                   stage_note=result["stage_note"],
                                                   system_qty=result["system_qty"],
                                                   os_ver=result["OS_Ver"],
                                                   buffer_activity=result["buffer"],
                                                   stage_begin=result["stage_begin"])
        elif result["stage_begin"] == "":
            models.ControlTableList.objects.create(project_stage=result["project_stage"],
                                                   project_id=result["project_id"],
                                                   stage_sku_qty=result["stage_sku_qty"],
                                                   stage_note=result["stage_note"],
                                                   system_qty=result["system_qty"],
                                                   os_ver=result["OS_Ver"],
                                                   buffer_activity=result["buffer"],
                                                   stage_end=result["stage_end"])
        else:
            models.ControlTableList.objects.create(project_stage=result["project_stage"],
                                                   project_id=result["project_id"],
                                                   stage_sku_qty=result["stage_sku_qty"],
                                                   stage_note=result["stage_note"],
                                                   system_qty=result["system_qty"],
                                                   os_ver=result["OS_Ver"],
                                                   buffer_activity=result["buffer"],
                                                   )
        return redirect('project_ct_info',nid)


def project_ct_content(request,lid):
    plist = models.ControlTableList.objects.filter(id=lid).values().first()
    pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
    sheets_list = T.Sheet.objects.all()
    case_list = T.TestCase.objects.all()
    test_user = U.UserInfo.objects.all().order_by('job_name')
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
    res_list = models.TestResult.objects.filter(ControlTableList_id=lid).values('sheet_id', 'test_result','remark','issue')
    sheet_result_list = {}
    bugid_dic={}
    attend_time_dic = {}
    test_sku_num_list = {}
    for i in sheets_list:
        re_list = []
        bugid_list=[]
        final_result = ''
        for j in res_list:
            if i.id == int(j['sheet_id']):
                if 'Refer to bug ' in j['remark']:
                    # bugid_list.append(int(re.findall(r"\d+",j['remark'])[0])) # 取 bug ID
                    bugid_list.append(j['issue'])
                    bugid_list = list(set(bugid_list)) # 列表去重
                    bugid_list.sort(reverse = False) # 排序
                re_list.append(j['test_result'])
                if 'Fail' in re_list:
                    final_result = 'Fail'
                elif re_list == []:
                    final_result = ''
                elif re_list != [] and 'Pass' not in re_list and 'Fail' not in re_list:
                    final_result = 'N/A'
                else:
                    final_result = 'Pass'

        bugid_dic[i.id] = bugid_list
        sheet_result_list[i.sheet_name] = final_result

        i.count = cout[i.sheet_name]
        # *******计算非N/A的SKU的sku数量*********
        test_sku_num = 0
        x = models.ControlTableContent.objects.filter(ControlTable_List_id=lid, sheet_id=i.id)
        for j in x:
            if j.tester.job_name != "N/A":
                test_sku_num += 1
        test_sku_num_list.update({i.id: test_sku_num})
        attend_time_dic.update({i.id: float(
            T.Sheet.objects.filter(id=i.id).values().first()["attend_time"]) * int(test_sku_num_list[i.id])})

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
                    finished_attend_time += float(j.test_case.attend_time)
            if attend_time_dic[i.sheet_id_id] != 0:
                finished_attend_time_dic.update({"sku"+str(k):'{:.0%}'.format(finished_attend_time / float(T.Sheet.objects.filter(id=i.sheet_id_id).values().first()["attend_time"]))})
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
    return render(request, 'Project/project_ct_content.html', {"test_user":test_user,"pj": pj, "plist": plist,
                                                               "SKU_Num_list": SKU_Num_list,"new_list":new_list,"SKU_num":int(plist['stage_sku_qty'])})


def test_result(request,sid,lid,skunum):  # lid:Controltable_list_id , sid:sheet_id,
    if request.method == "GET":
        plist = models.ControlTableList.objects.filter(id=lid).values().first()
        pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
        cases = T.TestCase.objects.filter(sheet_id=sid).order_by('case_id')
        name = T.Sheet.objects.filter(id=sid).values().first()['sheet_name']

        for i in cases:
            buglist = []

            if models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=sid,test_case_id=i.id,sku_num=skunum).values().first():
                i.result = models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=sid,test_case_id=i.id,sku_num=skunum).values().first()["test_result"]
                i.remark = models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=sid,test_case_id=i.id,sku_num=skunum).values().first()["remark"]
                i.issue = models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=sid,test_case_id=i.id,sku_num=skunum).values().first()["issue"]
                if i.issue:
                    bug_list = i.issue.split(",")
                    for k in bug_list:
                        if k == ",":
                            continue
                        else:
                            buglist.append(int(k))
                    i.buglist = buglist
                    bug_description = {}
                    for j in buglist:
                        bug = models.Issue.objects.filter(project_id=plist["project_id"], issue_id=j).all().values().first()
                        bug_description[j] = bug["description"]
                    i.bug_description = bug_description
                else:    i.bug_description =""
            else:
                i.result = ""
                i.remark = ""
                i.issue = ""

        if models.sheet_prepared.objects.filter(sheet_id=sid,ControlTable_List_id=lid).values():
            sheet_prepare = models.sheet_prepared.objects.filter(sheet_id=sid,ControlTable_List_id=lid).values().first()['sheet_prepared']
        else:sheet_prepare = T.Sheet.objects.filter(id=sid).values().first()['sheet_prepare']
        return render(request, "Project/test_result.html", {"case_list": cases,"name":name,"pj":pj,"plist":plist,"skunum":skunum,'sheet_prepare':sheet_prepare,'sid':sid})
    else:
        print(request.POST)
        project = models.ControlTableList.objects.filter(id=lid).values('project_id').first()
        result_info_id = models.ProjectInfo.objects.filter(project_id=project['project_id']).values("id").last()
        if request.POST.get("test_result"):

            if models.TestResult.objects.filter(ControlTableList_id=lid, sku_num=skunum, test_case_id=int(request.POST.get("case_id"))):
                if models.TestResult.objects.filter(ControlTableList_id=lid, sku_num=skunum, test_case_id=int(request.POST.get("case_id"))).values().first()["test_result"] != "Fail":
                    models.TestResult.objects.filter(ControlTableList_id=lid, sku_num=skunum,
                                                 test_case_id=int(request.POST.get("case_id"))).update(
                                                 test_result=request.POST.get("test_result"), tester_id=request.user.id,
                                                 result_info_id=result_info_id['id'])
                else:
                    models.TestResult.objects.filter(ControlTableList_id=lid, sku_num=skunum,
                                                     test_case_id=int(request.POST.get("case_id"))).update(
                        test_result=request.POST.get("test_result"), tester_id=request.user.id,
                        result_info_id=result_info_id['id'],issue="")

            else:

                models.TestResult.objects.create(ControlTableList_id=lid, sku_num=skunum, test_case_id=int(request.POST.get("case_id")),
                                                         test_result=request.POST.get("test_result"),tester_id=request.user.id,sheet_id=sid,
                                                       result_info_id = result_info_id['id'])


        elif request.POST.get("remark") or request.POST.get("remark") == "":

            if models.TestResult.objects.filter(ControlTableList_id=lid, sku_num=skunum,
                                                test_case_id=int(request.POST.get("case_id"))):
                models.TestResult.objects.filter(ControlTableList_id=lid, sku_num=skunum,
                                                test_case_id=int(request.POST.get("case_id"))).update(
                    remark=request.POST.get("remark"))
            else:
                models.TestResult.objects.create(ControlTableList_id=lid, sku_num=skunum,
                                                 test_case_id=int(request.POST.get("case_id")),
                                                 test_result="", tester_id=request.user.id,
                                                 sheet_id=sid,
                                                 result_info_id=result_info_id['id'],remark=request.POST.get("remark"))
        elif request.POST.get("prepare"):
            print("111111111111111")
            if models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid):
                models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid).update(
                        sheet_prepared=request.POST.get('prepare'))
            else:
                models.sheet_prepared.objects.create(
                        sheet_prepared=request.POST.get('prepare'),sheet_id=sid,ControlTable_List_id=lid)

        return redirect('test_result', lid=lid,sid=sid,skunum=skunum)
    # else:
    #     # case id 与 result组成字典后加到数据库
    #     project = models.ControlTableList.objects.filter(id=lid).values('project_id').first()
    #     case_id_list=request.POST.getlist('case_id')
    #     result_list=request.POST.getlist('test_result')
    #     remark_list=request.POST.getlist('remark')
    #     result=dict(zip(case_id_list,result_list))
    #     for i in result:
    #        if result[i] == 'custom':
    #           result[i] = request.POST.get('custom-input'+i)
    #     remark_result=dict(zip(case_id_list,remark_list))
    #     result_info_id = models.ProjectInfo.objects.filter(project_id=project['project_id']).values("id").last()
    #     if models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid).values():
    #         models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid).update(sheet_prepared=request.POST.get('prepare'))
    #     else:
    #         if request.POST.get('prepare'):
    #             models.sheet_prepared.objects.create(ControlTable_List_id=lid, sheet_id=sid,
    #                                              sheet_prepared=request.POST.get('prepare'))
    #     for i in result:
    #         if result[i] != "":
    #             models.TestResult.objects.create(ControlTableList_id=lid,sku_num=skunum,test_case_id=int(i),
    #                                              test_result=result[i],tester_id=request.user.id,sheet_id=sid,
    #                                              remark=remark_result[i],result_info_id = result_info_id['id'])
    #
    #         else:
    #             pass
    #         # result_info_id = result_info_id['id']
    #     return redirect('task_table',lid=lid)


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
    sheet_id_list = []
    for cases in case_list:
        sheet_list.append(cases.sheet.sheet_name)
        # sheet_id_list.append(cases.sheet.id)
    cout = Counter(sheet_list)
    # cout_id=Counter(sheet_id_list)
    case_count_list = {}
    # sheet的测试结果，若都Pass则Pass ，有一个fail则结果显示fail，若全部N/A,才写N/A，若有没有填结果的case则显示为空
    res_list = models.TestResult.objects.filter(ControlTableList_id=lid).values('sheet_id', 'test_result')
    sheet_result_list = {}

    for i in sheets_list:
        case_count_list.update({i.id:cout[i.sheet_name]})
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
    test_sku_num_list = {}
    done_count_list={}
    for sheets in sheets_list:
        sheets.count = cout[sheets.sheet_name]
        # *******计算非N/A的SKU的sku数量*********
        test_sku_num = 0
        x = models.ControlTableContent.objects.filter(ControlTable_List_id=lid, sheet_id=sheets.id)
        for j in x:
            if j.tester.job_name != "N/A":
                test_sku_num += 1
        test_sku_num_list.update({sheets.id: test_sku_num})
        # *************************************
        cases_by_sheet = T.TestCase.objects.filter(sheet_id=sheets.id).values('attend_time')
        attend_time_sum = 0
        for i in cases_by_sheet:
            attend_time_sum += float(i['attend_time'])
        attend_time_dic.update({sheets.id: attend_time_sum * int(test_sku_num_list[sheets.id] )}) # int(plist['stage_sku_qty']
        # attend_time_dic.update({sheets.id: attend_time_sum}) # 每个sheet总的attend time

    content_list = models.ControlTableContent.objects.filter(ControlTable_List_id=lid)
    new_list = []
    new_dic = {}
    # 将每个sheet所有SKU信息整合到同个字典中方便使用
    count = 0
    c=1
    for i in content_list:
        count += 1
        if count % int(plist['stage_sku_qty']) != 0: # 余数即为SKU num
            done_count_list.update({str(i.sheet_id_id) + 'sku' + str(count % int(plist['stage_sku_qty'])):models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i.sheet_id_id,sku_num= str(count % int(plist['stage_sku_qty']))).count()})

            new_dic.update({'sheet_id': i.sheet_id_id, 'sheet_name': i.sheet_id.sheet_name,'attend_time':attend_time_dic[i.sheet_id_id],
                            'sheet_description': i.sheet_id.sheet_description})
            new_dic.update({'sku' + str(count % int(plist['stage_sku_qty'])): i.tester.last_name})

            # 以test result中的数据个数和每个sheet的case个数做对比。相等 为finished，0为未开始做,中间为ongoing
            if done_count_list[str(i.sheet_id_id) + 'sku' + str(count % int(plist['stage_sku_qty']))] == case_count_list[i.sheet_id_id]:
                new_dic.update({'sku' + str(count % int(plist['stage_sku_qty'])) + 'done':"finished"})
            else:

                if done_count_list[str(i.sheet_id_id) + 'sku' + str(count % int(plist['stage_sku_qty']))] != 0:
                    new_dic.update({'sku' + str(count % int(plist['stage_sku_qty'])) + 'done': "ongoing"})
                else:
                    new_dic.update({'sku' + str(count % int(plist['stage_sku_qty'])) + 'done': "no"})


        if count % int(plist['stage_sku_qty']) == 0: # 余数为 0时 ，sku num即为 SKU 数量
            done_count_list.update({str(i.sheet_id_id) + 'sku' + str(
                int(plist['stage_sku_qty'])): models.TestResult.objects.filter(ControlTableList_id=lid,
                                                                                       sheet_id=i.sheet_id_id,
                                                                                       sku_num=str(int(plist['stage_sku_qty']))).count()})
            new_dic.update({'sku' + str(int(plist['stage_sku_qty'])): i.tester.last_name,'test_result':sheet_result_list[i.sheet_id.sheet_name]})

            if done_count_list[str(i.sheet_id_id) + 'sku' + str(int(plist['stage_sku_qty']))] == \
                    case_count_list[i.sheet_id_id]:
                new_dic.update({'sku' + str(int(plist['stage_sku_qty'])) + 'done': "finished"})
            else:
                if done_count_list[str(i.sheet_id_id) + 'sku' + str(int(plist['stage_sku_qty']))] != 0:
                    new_dic.update({'sku' + str(int(plist['stage_sku_qty'])) + 'done': "ongoing"})
                else:
                    new_dic.update({'sku' + str(int(plist['stage_sku_qty'])) + 'done': "no"})
            new_list.append(dict(new_dic))  # 字典更新会让list同步更新，需要将整个字典赋值

    # 每个sheet中的case个数
    # 检测result结果中该list中此sheet此sku有无结果
    # done_reuslt_list={}
    # sku_list=[]
    # done_result_sku = models.TestResult.objects.filter(ControlTableList_id=lid).values('sku_num').distinct()
    # for i in done_result_sku:
    #     sku_list.append(int(i['sku_num']))
    # for k in sku_list:
    #     sh_list = []
    #     done_result_sheet = models.TestResult.objects.filter(ControlTableList_id=lid).values('sheet','sku_num').distinct()
    #     for i in done_result_sheet:
    #         if int(i['sku_num'])==k:
    #             sh_list.append(i['sheet'])
    #     done_reuslt_list[k]=sh_list
    # print(done_reuslt_list)

    for i in new_list:
        if request.user.last_name in i.values():
            i['display']="display"
        else:
            i['display'] = "no-display"


    return render(request, 'Project/task_table.html', {"pj": pj, "plist": plist,"SKU_Num_list": SKU_Num_list,"new_list": new_list,"case_count_list":case_count_list})


def task_list(request):
    CT_lists=[]
    CT = models.ControlTableContent.objects.filter(tester_id=request.user.id).values_list('ControlTable_List_id_id',flat=True).distinct()
    for i in CT:
        CT_list=models.ControlTableList.objects.filter(id=i).values().first()
        CT_lists.append(CT_list)
    for i in CT_lists:
        project = models.Project.objects.filter(id=i['project_id']).values().first()
        i['project']=project
        # *******计算tester在这个task下的attend time********
        list = models.ControlTableContent.objects.filter(ControlTable_List_id_id=i['id']).values_list("tester__job_name",
                                                                                                'sheet_id')
        attend_time_dic_persheet = {}
        tester_list = []
        test_time = {}
        for j in list:
            if j[0] not in tester_list:
                tester_list.append(j[0])
            cases_by_sheet = T.TestCase.objects.filter(sheet_id=j[1]).values('attend_time')
            attend_time_sum = 0
            # for k in cases_by_sheet:
            #     attend_time_sum += float(k['attend_time'])
            # attend_time_dic_persheet.update({j[1]: attend_time_sum})
            for v in tester_list:

                try:
                    if v == j[0]:
                        test_time.update({v: test_time[v] + float(T.Sheet.objects.filter(id=j[1]).values().first()["attend_time"])})
                except:
                    test_time.update({v: float(T.Sheet.objects.filter(id=j[1]).values().first()["attend_time"])})

        # i['test_time']=test_time[request.user.last_name]
        i['test_time']='%.1f' % (test_time[request.user.last_name]/60)
        # *************************************************
        # *******计算progress*******************************
        finish_case=models.TestResult.objects.filter(ControlTableList_id=i['id'],tester=request.user.id).values('test_case_id')
        finish_time = 0
        for j in finish_case:
            finish_time += float(T.TestCase.objects.filter(id=j['test_case_id']).values('attend_time').first()['attend_time'])
        i['finish_progress'] = '%.2f' % (finish_time/test_time[request.user.last_name]*100)
        # *************************************************
    return render(request,'Project/task_list.html',{"CT_list":CT_lists})


def result_review(request,lid,sid,skunum):
    plist = models.ControlTableList.objects.filter(id=lid).values().first()
    pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
    name = T.Sheet.objects.filter(id=sid).values().first()['sheet_name']
    cases = T.TestCase.objects.filter(sheet_id=sid)
    result = models.TestResult.objects.filter(ControlTableList_id=lid, sheet_id=sid, sku_num=skunum, )
    buglist=[]
    if models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid).values():
        sheet_prepare = models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid).values().first()[
            'sheet_prepared']
    else:
        sheet_prepare = T.Sheet.objects.filter(id=sid).values().first()['sheet_prepare']
    result_list = []
    for j in cases:
        result_dic = {'case_id': j.id, 'test_case_id': j.case_id, 'case_name': j.case_name,
                      'procedure': j.procedure, 'pass_criteria': j.pass_criteria, 'result': ''}
        for i in result:
            if i.test_case.id == j.id:
                result_dic['result_id'] = i.id
                result_dic['result'] = i.test_result
                result_dic['remark'] = i.remark
                if i.issue:
                    bug_list = i.issue.split(",")
                    for k in bug_list:
                        if k == ",":
                            continue
                        else:
                            buglist.append(int(k))
                    result_dic['issue'] = buglist
                if "Refer to bug " in i.remark:
                    result_dic['bug_id'] = int(re.findall(r"\d+", i.remark)[0])
                # else:result_dic['bug_id'] = ''
        result_list.append(result_dic)
    if request.method == 'GET':
        bug_description = {}
        for i in buglist:
            bug = models.Issue.objects.filter(project_id=plist["project_id"],issue_id=i).all().values().first()
            bug_description[i] = bug["description"]
        return render(request,'Project/result_review.html',{'result_list':result_list,"pj": pj, "plist": plist,"cases":cases,"skunum":skunum,"name":name,'sid':sid,'sheet_prepare':sheet_prepare,'bug_description':bug_description})
    else:

        project = models.ControlTableList.objects.filter(id=lid).values('project_id').first()

        result_info_id = models.ProjectInfo.objects.filter(project_id=project['project_id']).values("id").last()
        case_id_list = request.POST.getlist('case_id')
        result_testlist = request.POST.getlist('test_result')
        issueid_list= request.POST.getlist('fail_bug_id')
        result = dict(zip(case_id_list, result_testlist))

        remark_list = request.POST.getlist('remark')
        result_remark = dict(zip(case_id_list, remark_list))
        result_issueidlist = dict(zip(case_id_list,issueid_list))
        models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid).update(sheet_prepared=request.POST.get('prepare'))
        for i in result:
            if result[i] == 'custom':
                if request.POST.get('custom-input' + i):
                    result[i] = request.POST.get('custom-input' + i)

            if result[i] =="" :
                models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                     sku_num=skunum).update(remark=result_remark[i])
            else:
                if models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=i,sku_num=skunum):
                    # models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=i,sku_num=skunum).update(test_result=result[i],result_info_id=result_info_id['id'],tester_id=request.user.id,)
                    if result[i] == 'Pass' and "Refer to bug " in result_remark[i]:
                        models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                         sku_num=skunum).update(test_result='Pass',remark='',issue="")
                        # models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                        #                                  sku_num=skunum).update(remark='')
                    elif result[i] == 'Pass':
                        models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                         sku_num=skunum).update(test_result='Pass',remark=result_remark[i],issue="")
                    elif result[i] == "Fail":
                        if result_issueidlist[i]:

                            bug = models.Issue.objects.filter(project_id=project['project_id'],
                                                              issue_id=result_issueidlist[i]).values().first()

                            if bug:

                                models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                                 sku_num=skunum).update(test_result=result[i],
                                                                                        result_info_id=result_info_id['id'],
                                                                                        tester_id=request.user.id,
                                                                                        remark='Refer to bug '+result_issueidlist[i]+":"+bug["description"])
                                # models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                #                                  sku_num=skunum).update(test_result=result[i], result_info_id=result_info_id['id'],tester_id=request.user.id, )

                            elif bug =="":

                                models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                                 sku_num=skunum).update(test_result='Fail',
                                                                                        remark=result_remark[i])
                            else:
                                messages.error(request, "查无此bugID ，请确认重新输入")

                                return render(request, 'Project/result_review.html',
                                              {'result_list': result_list, "pj": pj, "plist": plist, "cases": cases,

                                               "skunum": skunum, "name": name, 'sid': sid,'sheet_prepare':sheet_prepare})
                        else:
                            models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                             sku_num=skunum).update(test_result=result[i],
                                                                                    result_info_id=result_info_id['id'],
                                                                                    tester_id=request.user.id,remark=result_remark[i])
                    elif result[i] == "N/A":
                        models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                         sku_num=skunum).update(test_result='N/A', remark=result_remark[i])
                    else:
                        models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                         sku_num=skunum).update(test_result=result[i],remark=result_remark[i])
                else:
                    models.TestResult.objects.create(ControlTableList_id=lid, sku_num=skunum, test_case_id=int(i),
                                                     test_result=result[i], tester_id=request.user.id, sheet_id=sid,result_info_id=result_info_id['id'],remark=result_remark[i])
        return redirect("task_table",lid=lid)


def result_check(request,lid,sid,skunum):
    plist = models.ControlTableList.objects.filter(id=lid).values().first()
    pj = models.Project.objects.filter(id=plist["project_id"]).values().first()
    name = T.Sheet.objects.filter(id=sid).values().first()['sheet_name']
    cases = T.TestCase.objects.filter(sheet_id=sid)
    result = models.TestResult.objects.filter(ControlTableList_id=lid, sheet_id=sid, sku_num=skunum, )
    result_list = []
    buglist = []
    for j in cases:
        result_dic = {'case_id': j.id, 'test_case_id': j.case_id, 'case_name': j.case_name,
                      'procedure': j.procedure, 'pass_criteria': j.pass_criteria, 'result': ''}
        for i in result:
            if i.test_case.id == j.id:
                result_dic['result_id'] = i.id
                result_dic['result'] = i.test_result
                result_dic['remark'] = i.remark
                if i.issue:
                    bug_list = i.issue.split(",")
                    for k in bug_list:
                        if k == ",":
                            continue
                        else:
                            buglist.append(int(k))
                    result_dic['issue'] = buglist
                if "Refer to bug " in i.remark:
                    result_dic['bug_id'] = int(re.findall(r"\d+", i.remark)[0])
                # else:result_dic['bug_id'] = ''
        result_list.append(result_dic)

    if request.method == 'GET':
        if models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid).values():
            sheet_prepare = \
            models.sheet_prepared.objects.filter(sheet_id=sid, ControlTable_List_id=lid).values().first()[
                'sheet_prepared']
        else:
            sheet_prepare = T.Sheet.objects.filter(id=sid).values().first()['sheet_prepare']
        bug_description = {}
        for i in buglist:
            bug = models.Issue.objects.filter(project_id=plist["project_id"], issue_id=i).all().values().first()
            bug_description[i] = bug["description"]
        return render(request, 'Project/result_check.html',
                      {'result_list': result_list, "pj": pj, "plist": plist, "cases": cases, "skunum": skunum,
                       "name": name, 'sid': sid,'sheet_prepare':sheet_prepare,'bug_description':bug_description})
    else:
        models.sheet_prepared.objects.filter(sheet_id=sid,ControlTable_List_id=lid).update(
            sheet_prepared=request.POST.get('prepare'))
        # plist = models.ControlTableList.objects.filter(id=lid).values().first()
        project = models.ControlTableList.objects.filter(id=lid).values('project_id').first()
        result_info_id = models.ProjectInfo.objects.filter(project_id=project['project_id']).values("id").last()
        case_id_list = request.POST.getlist('case_id')
        result_testlist = request.POST.getlist('test_result')
        issueid_list = request.POST.getlist('fail_bug_id')
        result = dict(zip(case_id_list, result_testlist))
        remark_list = request.POST.getlist('remark')
        result_remark = dict(zip(case_id_list, remark_list))
        result_issueidlist = dict(zip(case_id_list, issueid_list))
        for i in result:
            if result[i] == 'custom':
                result[i] = request.POST.get('custom-input' + i)
        for i in result:
            if result[i] =="":
                continue
            elif models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i, sku_num=skunum):
                # models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=i,sku_num=skunum).update(test_result=result[i],result_info_id=result_info_id['id'],tester_id=request.user.id,)
                if result[i] == 'Pass' and "Refer to bug " in result_remark[i]:
                    models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                     sku_num=skunum).update(test_result='Pass',remark='',issue="")
                elif result[i] == 'Pass':
                    models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                     sku_num=skunum).update(test_result='Pass')
                elif result[i] == "Fail":

                    if result_issueidlist[i]:
                        bug = models.Issue.objects.filter(project_id=project['project_id'],
                                                          issue_id=result_issueidlist[i]).values().first()
                        if bug:
                            models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                             sku_num=skunum).update(
                                remark='Refer to bug ' + result_issueidlist[i] + ":" + bug["description"])
                            models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                             sku_num=skunum).update(test_result=result[i],
                                                                                    result_info_id=result_info_id['id'],
                                                                                    tester_id=request.user.id, )
                        elif bug == "":
                            models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                             sku_num=skunum).update(test_result='Fail',
                                                                                    remark=result_remark[i])
                        else:

                            messages.error(request, "查无此bugID ，请确认重新输入")

                            return render(request, 'Project/result_check.html',
                                          {'result_list': result_list, "pj": pj, "plist": plist, "cases": cases,
                                           "skunum": skunum,
                                           "name": name, 'sid': sid})
                    else:
                        models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                         sku_num=skunum).update(test_result=result[i],
                                                                                result_info_id=result_info_id['id'],
                                                                                tester_id=request.user.id,
                                                                                remark=result_remark[i])
                elif result[i] == "N/A":
                    models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                     sku_num=skunum).update(test_result='N/A', remark='')



                else:
                    models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=i,
                                                     sku_num=skunum).update(test_result=result[i])

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
        models.ControlTableList.objects.filter(id=lid).update(project_stage=request.POST.get("project_stage"),
                                                              stage_sku_qty=request.POST.get("stage_sku_qty"),
                                                              stage_begin=request.POST.get("stage_begin"),
                                                              stage_end=request.POST.get("stage_end"),
                                                              stage_note=request.POST.get("stage_note"),
                                                              system_qty=request.POST.get("system_qty"),
                                                              OS_Ver=request.POST.get("OS_Ver"),
                                                              buffer_activity=request.POST.get("buffer"),
                                                              )
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
        pj_info = models.ProjectInfo.objects.filter(project_id=pj["id"]).values().last()
        return render(request, 'Project/add_issue.html', {"pj": pj,"pj_info":pj_info})
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
        # return HttpResponse("OK")


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
        test_user = U.UserInfo.objects.all().order_by('job_name')
        return render(request,"Project/change_tester.html",{"test_user":test_user,"lid":lid,"sid":sid,"skunum":skunum})
    else:
        models.ControlTableContent.objects.filter(ControlTable_List_id_id=lid,sheet_id_id=sid,sku_num=skunum).update(
            tester=request.POST.get("changed_tester")
        )
        return redirect("/")
        # return redirect("project_ct_content",lid)


# def combine(temp_list, n):
#     from itertools import combinations
#     '''根据n获得列表中的所有可能组合（n个元素为一组）'''
#     temp_list2 = []
#     for c in combinations(temp_list, n):
#         temp_list2.append(c)
#     return temp_list2

def assign_bug(request,pid,lid,cid,sid,skunum):
    if request.method == "GET":
        return render(request, 'Project/assign_bug.html',{"pid":pid,"lid":lid,"cid":cid,"sid":sid,"skunum":skunum})
    else:
        if request.POST.get("assign_bug"):
            if ',' in request.POST.get("assign_bug"):
                bug_list=request.POST.get("assign_bug").split(",")
            else:
                bug_list=[]
                bug_list.append(request.POST.get("assign_bug"))

            buglist=""
            for i in bug_list:
                try:
                    bug=models.Issue.objects.filter(project_id=pid,issue_id=int(i)).values().first()
                except ValueError:
                    messages.error(request, "输入错误")
                else:
                    if bug:
                        if buglist == "":
                            buglist = i
                        else:buglist = buglist + "," + i
                        # if "Refer to bug " in models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=cid,sku_num=skunum).values().first()["remark"]:
                        #     if "bug " + i + ":" + bug["description"] in models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=cid,sku_num=skunum).values().first()["remark"]:
                        #         continue
                        #
                        #     else:models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=cid, sku_num=skunum).update(
                        #             remark=models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=cid,sku_num=skunum).values().first()["remark"]+";"+'\n' + "bug " + i + ":" + bug["description"])
                        # else:models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=cid, sku_num=skunum).update(
                        #         remark="Refer to " +'\n' "bug " + i + ":"+ bug["description"])

                        models.TestResult.objects.filter(ControlTableList_id=lid, test_case_id=cid, sku_num=skunum).update(
                            issue=buglist)
                    else:
                        messages.error(request, "查无 ID 为 "+i+" 的bug,请确认重新添加")
                        return redirect("test_result", lid, sid, skunum)

            return redirect("test_result", lid, sid, skunum)
            #     models.TestResult.objects.filter(ControlTableList_id=lid,test_case_id=cid,sku_num=skunum).update(remark="Refer to bug "+request.POST.get("assign_bug")+":"+bug["description"])
            # else:messages.error(request, "查无此bugID ，请确认重新输入")
            # return redirect("result_review",lid,sid,skunum)
            # return HttpResponse("hello")
        else:
            messages.success(request, "输入错误")
            return redirect("test_result",lid,sid,skunum)


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
                wrap on,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 52 ;
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
                fore-colour 52 ;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

        style_heading_4 = xlwt.easyxf(
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
                fore-colour 52 ;
        
            """)
        style_heading_3 = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index blue,
                bold on,
                height 0x0120,
                italic True;
            align:
                wrap on,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 52 ;
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

        style_body_2 = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index blue,
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
        style_body_3 = xlwt.easyxf(
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
        style_body_4 = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index black,
                bold on,
                height 0xDD;
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
        style_result_NA = xlwt.easyxf(
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
            pattern:
                pattern solid,
                fore-colour 22 ;
            """)
        style_result_N = xlwt.easyxf(
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
                fore-colour 52 ;    
            """)
        style_prepare = xlwt.easyxf(
            """
            font:
                name Arial,
                colour_index black,
                bold on,
                height 0xC8;
            align:
                wrap on,
                vert center,
                horiz left;
            pattern:
                pattern solid,
                fore-colour 26 ;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

        style_heading_5 = xlwt.easyxf(
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
                fore-colour 52 ;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;

            """,num_format_str='0.00%')



        # ***********************************************
        # ***********************************************
        # 生成table of Contents
        project_stage=models.ControlTableList.objects.filter(id=lid).values().first()['project_stage']
        project_id=models.ControlTableList.objects.filter(id=lid).values().first()['project_id']
        project=models.Project.objects.filter(id=project_id).values().first()
        w_c = ws.add_sheet('Table_of_Contents',cell_overwrite_ok=True)
        w_c.insert_bitmap('../logo.bmp',1,8,scale_x=0.15,scale_y=0.49)

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
        w_c.write_merge(0, 1, 0, 4,project['project_name']+' '+project['project_model'].replace(',','_')+' '+project_stage+' Compatibility Test Report',style_heading)
        w_c.row(0).height_mismatch = True
        w_c.row(0).height = 700
        w_c.write_merge(2, 3, 0, 4,'Project:'+' '+project['project_name']+' '+project['project_model'],style_heading)
        # w.write_merge(2, 3, 0, 0,'',style_title1)
        w_c.write_merge(0, 3, 5, 5 + int(sku_n),'',style_heading)
        # w_c.write_merge(2, 3, 5, 5 + int(sku_n),'',style_heading)
        excel_row_C = 6

        # 对每个sheet进行生成
        for i in sheets_list:
            w = ws.add_sheet(i.sheet_name,cell_overwrite_ok=True)


            w.write(6, 0, 'Case_ID',style_heading_2)
            w.write(6, 1, 'Case_Name',style_heading_2)
            w.write(6, 2, 'Procedure',style_heading_2)
            w.write(6, 3, 'Pass_Critearia',style_heading_2)
            k = 0
            while k<int(sku_n):
                w.write(0, 0,xlwt.Formula('HYPERLINK("#Table_of_Contents!A1","Go Back")'),style_back)
                w.write_merge(0, 0, 1, 5 + k, 'Test Suite:' + i.sheet_name,style_heading_2)
                # w.write(1, 0, "",style_heading_2)
                w.write_merge(1, 1, 0, 5 + k, i.sheet_description,style_heading_3)
                w.write(6, 4+k, 'SKU'+str(k+1),style_heading_2)
                w.col(4 + k).width = 1500
                k+=1
            # w.write(2, 4, 'SKU1')
            w.write(6, 4+int(sku_n), 'Notes/Comment',style_heading_2)

            w.col(0).width = 3500
            w.col(1).width = 5000
            w.col(2).width = 15000
            w.col(3).width = 15000
            w.col(4 + int(sku_n)).width = 13000

            # *********preparation***************
            if models.sheet_prepared.objects.filter(ControlTable_List_id=lid, sheet_id=i.id):
                excel_row = 8
                sheet_prepare=models.sheet_prepared.objects.filter(ControlTable_List_id=lid,sheet_id=i.id).values().first()['sheet_prepared']
                w.write_merge(excel_row-1, excel_row-1, 0, 1, 'Preparation', style_prepare)
                w.write_merge(excel_row-1, excel_row-1, 2, 4 + int(sku_n), sheet_prepare, style_prepare)
                w.row(excel_row-1).height_mismatch = True
                w.row(excel_row-1).height=2000
            else:excel_row = 7
            # ***********************************


            li=models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i.id).values_list('test_case_id').distinct()
            for x in li:
                # for j in result_list:
                case_id=T.TestCase.objects.filter(id=x[0]).values().first()['case_id']
                case_name=T.TestCase.objects.filter(id=x[0]).values().first()['case_name']
                procedure=T.TestCase.objects.filter(id=x[0]).values().first()['procedure']
                pass_criteria=T.TestCase.objects.filter(id=x[0]).values().first()['pass_criteria']
                # Notes_Comment=T.TestCase.objects.filter(id=x[0]).values().first()['remark']
                # 写入数据

                w.write(excel_row, 0, case_id,style_body_4)
                w.write(excel_row, 1, case_name,style_body_4)
                w.write(excel_row, 2, procedure,style_body_3)
                w.write(excel_row, 3, pass_criteria,style_body_3)
                # for l in  SKU_N_list:
                l = 1
                while l <= int(sku_n):
                    try:
                        result=models.TestResult.objects.filter(ControlTableList_id=lid,sheet_id=i.id,sku_num=str(l),test_case_id=x[0]).values().first()['test_result']
                    except :

                        if models.ControlTableContent.objects.filter(ControlTable_List_id=lid,sheet_id=i.id,sku_num=str(l)).values().first()['tester_id'] == 2:
                            result='N/A'
                        else:
                            result="-"
                    if result == "Pass":
                        w.write(excel_row, 3+l, result, style_result_pass)
                    elif result == "Fail":
                        w.write(excel_row, 3+l, result, style_result_fail)
                    else:
                        w.write(excel_row, 3+l, result, style_result_NA)
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
                        elif y['remark'] in notes:
                            continue
                        else:
                            notes=notes+';'+'\n'+ y['remark']
                w.write(excel_row, 4+int(sku_n), notes,style_body_3)

                # w.write(excel_row, 5, Notes_Comment)
                excel_row += 1

                # *************************************************
            w.write(2, 2, "Progress  %", style_heading_2)
            w.write(2, 3, xlwt.Formula('SUM(D4:D6)'), style_heading_5)
            w.write(3, 2, "Pass rate %", style_heading_2)
            w.write(3, 3, xlwt.Formula('COUNTIF(E8:$H200,"pass")/E4'), style_heading_5)

            w.write(4, 2, "Fail rate %", style_heading_2)
            w.write(4, 3, xlwt.Formula('COUNTIF(E8:$H200,"fail")/E4'), style_heading_5)
            w.write(5, 2, "N/A rate  %", style_heading_2)
            w.write(5, 3, xlwt.Formula('COUNTIF(E8:$H200,"N/A")/E4'), style_heading_5)
            w.write_merge(2, 2, 4, 3+int(sku_n), "Item", style_heading_2)
            w.write_merge(3,3, 4, 3+int(sku_n),  xlwt.Formula(
                'COUNTIF(E8:$H200,"pass")+COUNTIF(E8:$H200,"fail")+COUNTIF(E8:$H200,"N/A")+COUNTIF(E8:$H200,"-")'),
                          style_heading_2)
            w.write(2, 0, "", style_heading_4)
            w.write(2, 1, "", style_heading_4)
            w.write(3, 0, "", style_heading_4)
            w.write(3, 1, "", style_heading_4)
            w.write(4, 0, "", style_heading_4)
            w.write(4, 1, "", style_heading_4)
            w.write(5, 0, "", style_heading_4)
            w.write(5, 1, "", style_heading_4)
            w.write(2, 4+int(sku_n), "", style_heading_4)
            w.write(3, 4+int(sku_n), "", style_heading_4)
            w.write(4, 4+int(sku_n), "", style_heading_4)
            w.write(5, 4+int(sku_n), "", style_heading_4)
            w.write_merge(4, 5, 4, 3+int(sku_n), "SKU", style_heading_2)
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
                    if 'Refer to bug ' in j['remark']:
                        bugid_list.append(int(re.findall(r"\d+", j['remark'])[0]))  # 取 bug ID
                        bugid_list = list(set(bugid_list))  # 列表去重
                        bugid_list.sort(reverse=False)  # 排序
                    re_list.append(j['test_result'])
                    if 'Fail' in re_list:
                        final_result = 'Fail'
                    elif re_list == []:
                        final_result = ''
                    elif re_list != [] and 'Pass' not in re_list and 'Fail' not in re_list:
                        final_result = 'N/A'
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
                attend_time_sum += float(i['attend_time'])
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
                        finished_attend_time += float(j.test_case.attend_time)
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
                w_c.write(excel_row_C, 4, i['test_result'], style_result_N)
            k = 0
            while k < int(sku_n):
                # w.write(2, 4 + k, '')
                if i['sku' + str(k + 1) + '_progress'] == '100%':
                    w_c.write(excel_row_C, 5 + k, i['sku' + str(k + 1) + '_progress'], style_result_pass)
                else:
                    w_c.write(excel_row_C, 5 + k, i['sku' + str(k + 1) + '_progress'], style_result_fail)
                k += 1
            if i['bugid'] != []:
                w_c.write(excel_row_C, 5 + int(sku_n), 'Refer to bugID: ' + str(i['bugid']), style_body_3)
            else:
                w_c.write(excel_row_C, 5 + int(sku_n), '', style_body_3)
            excel_row_C += 1
        # 写出到IO
        sio = BytesIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')

        response['Content-Disposition'] = 'attachment; filename='+project['project_name']+' '+project['project_model'].replace(',','_')\
                                          +' '+project_stage+' Compatibility Test Report'+'_'\
                                          +str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))+'.xls'
        response.write(sio.getvalue())
        return response
            # redirect('project_ct_info', models.ControlTableList.objects.filter(id=lid).values().first()['project_id'])


def test_time_review(request,lid):
    list = models.ControlTableContent.objects.filter(ControlTable_List_id_id=lid).values_list("tester__job_name",'sheet_id')
    attend_time_dic_persheet = {}
    tester_list=[]
    test_time={}
    finish_progress={}
    review_data=[]
    for i in list:
        if i[0] not in tester_list:
            tester_list.append(i[0])
        cases_by_sheet = T.TestCase.objects.filter(sheet_id=i[1]).values('attend_time')
        attend_time_sum = 0
        for j in cases_by_sheet:
            attend_time_sum += float(j['attend_time'])
        attend_time_dic_persheet.update({i[1]: attend_time_sum})
        for k in tester_list:
            try:
                if k==i[0]:
                    test_time.update({k:test_time[k]+attend_time_dic_persheet[i[1]]})
            except:
                test_time.update({k:attend_time_dic_persheet[i[1]]})

    if "N/A" in tester_list:
        del test_time["N/A"]
    for i in test_time.keys():
        finish_case = models.TestResult.objects.filter(ControlTableList_id=lid, tester__last_name=i).values(
            'test_case_id')
        finish_time = 0

        for j in finish_case:

            finish_time += float(
                T.TestCase.objects.filter(id=j['test_case_id']).values('attend_time').first()['attend_time'])
        finish_progress[i] = '%.2f' % (finish_time/test_time[i]*100)
        review_data.append({"tester":i,"test_time":test_time[i],"progress":finish_progress[i]})

    return render(request, "project/test_time_review.html",{"test_time":test_time,"review_data":review_data})


def project_sum(request):
    if request.method == 'GET':
        # ********************************************
        now_date=datetime.datetime.now().strftime("%Y-%m-%d")
        str_time=datetime.datetime.now().strftime("%Y")+'-01-01'
        sum_project=[]
        pro_model_list=[]
        sum_model=0
        sum_at_time=0
        sum_buffer=0
        progress = {}
        stage_list=models.ControlTableList.objects.filter(stage_end__gte=str_time,stage_begin__lte=now_date).order_by("-stage_begin")


        # ********************************************

        for i in stage_list:
            i.attend_hours ='%.2f' % (float(i.attend_time) / 60)
            if i.buffer_activity == '':
                i.buffer_activity = '0%'
            sum_project.append(i.project.project_name)
            pro_model_list.append(i.project.project_model)
            sum_buffer += float(i.buffer_activity.split('%')[0])
            if i.attend_time != 0:
                progress.update({i.id: '{:.2%}'.format(float(i.finished_time) / float(i.attend_time))})
                sum_at_time += float(i.attend_hours)

            if i.attend_time == "N/A" or i.attend_time == "0":
                i.progressed = "N/A"
            else:
                i.progressed = '{:.2%}'.format(float(i.finished_time) / float(i.attend_time))
        for i in set(pro_model_list):
            if ',' in i:
                sum_model += len(i.split(','))
            else:sum_model += 1
        try:
            buffer_lev = sum_buffer / stage_list.count()
        except:
            buffer_lev = 0
        sum_list={"sum_project":len(list(set(sum_project))),"sum_model":sum_model,"sum_at_time":'%.2f' % (sum_at_time),"sum_buffer":'%.1f' % buffer_lev,"sum_stage":stage_list.count()}
        return render(request,'project/project_summary.html',{'sum_list':sum_list,'stage_list':stage_list,"now_date":now_date,"str_time":str_time})

    else:
        # ********************************************
        end_date = request.POST.get("search_endtime")
        str_date = request.POST.get("search_strtime")
        customer = request.POST.get("customer")
        sum_project = []
        pro_model_list = []
        sum_model = 0
        sum_at_time = 0
        sum_buffer = 0
        progress = {}
        if customer == '0':
            stage_list = models.ControlTableList.objects.filter(stage_end__gte=str_date,stage_begin__lte=end_date,
                                                                ).order_by("-stage_begin")
        else:
            stage_list = models.ControlTableList.objects.filter(stage_end__gte=str_date,stage_begin__lte=end_date,
                                                                project__project_type=customer).order_by("-stage_begin")
        # ********************************************
        for i in stage_list:
            i.attend_hours = '%.2f' % (float(i.attend_time) / 60)
            if i.buffer_activity == '':
                i.buffer_activity = '0%'

            sum_project.append(i.project.project_name)
            pro_model_list.append(i.project.project_model)
            sum_buffer += float(i.buffer_activity.split('%')[0])

            if i.attend_time != 0:
                progress.update({i.id: '{:.2%}'.format(float(i.finished_time) / float(i.attend_time))})

                sum_at_time += float(i.attend_hours)

            if i.attend_time == "N/A" or i.attend_time == "0":
                i.progressed = "N/A"
            else:
                i.progressed = '{:.2%}'.format(float(i.finished_time) / float(i.attend_time))
        for i in set(pro_model_list):
            if ',' in i:
                sum_model += len(i.split(','))
            else:sum_model += 1
        try:
            buffer_lev =sum_buffer/stage_list.count()
        except:
            buffer_lev = 0
        sum_list={"sum_project":len(list(set(sum_project))),"sum_model":sum_model,"sum_at_time":'%.2f' % (sum_at_time),"sum_buffer":'%.1f' % buffer_lev,"sum_stage":stage_list.count()}
        return render(request, 'project/project_summary.html',
                      {'sum_list': sum_list, 'stage_list': stage_list, "now_date": end_date, "str_time": str_date})


