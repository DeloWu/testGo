from ast import literal_eval
from autoTest import goFunction
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from .models import Project, Environment, Api, TestStep, TestCases, Report, Encryption, MockServer
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask
from django.template import Context
from httprunner import HttpRunner
import json
import locust
import logging
import os
import pprint
import requests
import time

# logger = logging.getLogger('testGo.app')
hrun_base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r'httprunner\tests\testcases')

'''
登录验证装饰器
def login_check(func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_status'):
            return HttpResponseRedirect('/api/login/')
        return func(request, *args, **kwargs)

    return wrapper
'''

# @cache_page(60 * 5)
def index(request):
    return render(request, 'autoTest/index.html', context={})


def pro_index(request):
    pro_sum = Project.objects.all().order_by('pro_id')
    paginator = Paginator(pro_sum, 10)
    page = request.GET.get('page', 1)
    current_page = int(page)
    try:
        pro_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        pro_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        pro_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if pro_list.has_previous():
        previous_page_index = pro_list.previous_page_number()
    else:
        previous_page_index = None
    if pro_list.has_next():
        next_page_index = pro_list.next_page_number()
    else:
        next_page_index = None
    return render(request, 'autoTest/pro_index.html', context={'pro_list': pro_list,
                                                               'paginator': paginator,
                                                               'current_page': current_page,
                                                               'previous_page_index': previous_page_index,
                                                               'next_page_index': next_page_index
                                                               })


def pro_add(request):
    if request.method == 'POST':
        pro_name = request.POST['pro_name']
        description = request.POST['description']
        pro = Project(pro_name=pro_name, description=description)
        pro.save()
        return HttpResponseRedirect("/autoTest/pro_index/")
    if request.method == 'GET':
        return render(request, 'autoTest/pro_add.html', context={})


def pro_delete(request):
    if request.method == 'GET':
        pro_id = request.GET['pro_id']
        Project.objects.filter(pro_id=pro_id).delete()
        return HttpResponseRedirect("/autoTest/pro_index/")



def pro_update(request):
    if request.method == 'POST':
        pro_id = request.POST['pro_id']
        pro_name = request.POST['pro_name']
        description = request.POST['description']
        Project.objects.filter(pro_id=pro_id).update(pro_name=pro_name, description=description)
        return HttpResponseRedirect("/autoTest/pro_index/")
    if request.method == 'GET':
        pro_id = request.GET['pro_id']
        pro = Project.objects.get(pro_id=pro_id)
        return render(request, 'autoTest/pro_update.html', context={"pro": pro})


def env_index(request):
    page = request.GET.get('page', 1)
    pro_id = request.GET.get('pro_id', '')
    pro_sum = Project.objects.all()
    if pro_id:
        project = Project.objects.get(pro_id=pro_id)
        env_sum = Environment.objects.filter(relative_pro=pro_id)
    else:
        project = None
        env_sum = Environment.objects.all().order_by('env_id')
    paginator = Paginator(env_sum, 10)
    current_page = int(page)
    try:
        env_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        env_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        env_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if env_list.has_previous():
        previous_page_index = env_list.previous_page_number()
    else:
        previous_page_index = None
    if env_list.has_next():
        next_page_index = env_list.next_page_number()
    else:
        next_page_index = None
    return render(request, 'autoTest/env_index.html', context={'env_list': env_list,
                                                               'paginator': paginator,
                                                               'current_page': current_page,
                                                               'previous_page_index': previous_page_index,
                                                               'next_page_index': next_page_index,
                                                               'pro_sum': pro_sum,
                                                               'cur_pro': project,
                                                               })


def env_add(request):
    if request.method == 'POST':
        env_name = request.POST['env_name']
        pro_id = request.POST['pro_id']
        url = request.POST['url']
        port = request.POST['port']
        description = request.POST['description']
        env = Environment(env_name=env_name, url=url, port=port, relative_pro=pro_id,
                          description=description)
        env.save()
        return HttpResponseRedirect("/autoTest/env_index/")
    if request.method == 'GET':
        pro_list = Project.objects.all()
        try:
            cur_env_id = request.GET['env_id']
            cur_env = Environment.objects.get(env_id=cur_env_id)
            cur_pro_id = cur_env.relative_pro
            cur_pro = Project.objects.get(pro_id=cur_pro_id)
        except:
            cur_pro = ''
        return render(request, "autoTest/env_add.html", {"pro_list": pro_list,
                                                         "cur_pro": cur_pro,
                                                         })


def env_delete(request):
    if request.method == 'GET':
        env_id = request.GET['env_id']
        Environment.objects.filter(env_id=env_id).delete()
        return HttpResponseRedirect("/autoTest/env_index/")


def env_update(request):
    if request.method == 'POST':
        env_id = request.POST['env_id']
        env_name = request.POST['env_name']
        pro_id = request.POST['pro_id']
        url = request.POST['url']
        port = request.POST['port']
        description = request.POST['description']
        Environment.objects.filter(env_id=env_id).update(env_name=env_name, url=url, port=port, relative_pro=pro_id,
                                                         description=description)
        return HttpResponseRedirect("/autoTest/env_index/")
    if request.method == 'GET':
        env_id = request.GET['env_id']
        env = Environment.objects.get(env_id=env_id)
        cur_pro = Project.objects.get(pro_id=env.relative_pro)
        pro_list = Project.objects.all()
        return render(request, "autoTest/env_update.html", {"env": env,
                                                            "pro_list": pro_list,
                                                            "cur_pro": cur_pro, })


def api_index(request):
    page = request.GET.get('page', 1)
    pro_id = request.GET.get('pro_id', '')
    pro_sum = Project.objects.all()
    if pro_id:
        project = Project.objects.get(pro_id=pro_id)
        api_sum = Api.objects.filter(relative_pro=pro_id).order_by('api_id')
    else:
        project = None
        api_sum = Api.objects.all().order_by('api_id')
    paginator = Paginator(api_sum, 10)
    current_page = int(page)
    try:
        api_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        api_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        api_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if api_list.has_previous():
        previous_page_index = api_list.previous_page_number()
    else:
        previous_page_index = None
    if api_list.has_next():
        next_page_index = api_list.next_page_number()
    else:
        next_page_index = None
    return render(request, 'autoTest/api_index.html', context={'api_list': api_list,
                                                               'paginator': paginator,
                                                               'current_page': current_page,
                                                               'previous_page_index': previous_page_index,
                                                               'next_page_index': next_page_index,
                                                               'pro_sum': pro_sum,
                                                               'cur_pro': project,
                                                               })


def api_add(request):
    if request.method == 'POST':
        api_name = request.POST['api_name']
        api_path = request.POST['api_path']
        if not api_path.endswith(r'/'):
            api_path = api_path + r'/'
        method = request.POST['method']
        content_type = request.POST['content_type']
        headers = request.POST['headers']
        body = request.POST['body']
        description = request.POST['description']
        validate = request.POST['validate']
        encry_flag = request.POST['encry_flag']
        encry_id = request.POST['encry_id']
        pro_id = request.POST['pro_id']
        necessaryFlag_dict = request.POST['necessaryFlag_dict']
        dataType_dict = request.POST['dataType_dict']
        description_dict = request.POST['description_dict']
        # 若content_type 为json或者x-www-form-urlencoded格式，自动添加请求头参数
        headers_eval = literal_eval(headers)
        if content_type == 'json':
            headers_eval['Content-Type'] = 'application/json'
            body = body.replace(' ','')
            body_eval = literal_eval(body)
            dataType_dict_eval = literal_eval(dataType_dict)
            necessaryFlag_dict_eval = literal_eval(necessaryFlag_dict)
            for item in list(body_eval.values()):
                necessaryFlag_dict_eval['body'].append('1')
                if isinstance(item,str):
                    dataType_dict_eval['body'].append('string')
                if isinstance(item,int):
                    dataType_dict_eval['body'].append('int')
                if isinstance(item,float):
                    dataType_dict_eval['body'].append('double')
                if isinstance(item,list):
                    dataType_dict_eval['body'].append('list')
                if isinstance(item,dict):
                    dataType_dict_eval['body'].append('dict')
            necessaryFlag_dict = str(necessaryFlag_dict_eval).replace("'", '"')
            dataType_dict = str(dataType_dict_eval).replace("'", '"')
        if content_type == 'x-www-form-urlencoded':
            headers_eval['Content-Type'] = 'application/x-www-form-urlencoded'
        headers_eval = str(headers_eval).replace("'", '"')
        api = Api(api_name=api_name, api_path=api_path, method=method, content_type=content_type, headers=headers_eval,
                  body=body, description=description, validate=validate, encry_flag=encry_flag, relative_enc=encry_id,
                  relative_pro=pro_id, necessaryFlag_dict=necessaryFlag_dict, dataType_dict=dataType_dict,
                  description_dict=description_dict)
        api.save()
        return HttpResponseRedirect("/autoTest/api_index/")
    if request.method == 'GET':
        pro_list = Project.objects.all()
        encry_list = Encryption.objects.all()
        return render(request, 'autoTest/api_add.html', context={"pro_list": pro_list,
                                                                 "encry_list": encry_list, })


def api_delete(request):
    if request.method == 'GET':
        api_id = request.GET['api_id']
        Api.objects.filter(api_id=api_id).delete()
        return HttpResponseRedirect("/autoTest/api_index/")


def api_update(request):
    if request.method == 'POST':
        api_id = request.POST['api_id']
        api_name = request.POST['api_name']
        api_path = request.POST['api_path']
        if not api_path.endswith(r'/'):
            api_path = api_path + r'/'
        method = request.POST['method']
        content_type = request.POST['content_type']
        headers = request.POST['headers']
        body = request.POST['body']
        description = request.POST['description']
        validate = request.POST['validate']
        encry_flag = request.POST['encry_flag']
        encry_id = request.POST['encry_id']
        pro_id = request.POST['pro_id']
        necessaryFlag_dict = request.POST['necessaryFlag_dict']
        dataType_dict = request.POST['dataType_dict']
        description_dict = request.POST['description_dict']
        # 若content_type 为json或者x-www-form-urlencoded格式，自动添加请求头参数
        headers_eval = literal_eval(headers)
        if content_type == 'json':
            headers_eval['Content-Type'] = 'application/json'
            body = body.replace(' ', '')
            body_eval = literal_eval(body)
            dataType_dict_eval = literal_eval(dataType_dict)
            necessaryFlag_dict_eval = literal_eval(necessaryFlag_dict)
            for item in list(body_eval.values()):
                necessaryFlag_dict_eval['body'].append('1')
                if isinstance(item, str):
                    dataType_dict_eval['body'].append('string')
                if isinstance(item, int):
                    dataType_dict_eval['body'].append('int')
                if isinstance(item, float):
                    dataType_dict_eval['body'].append('double')
                if isinstance(item, list):
                    dataType_dict_eval['body'].append('list')
                if isinstance(item, dict):
                    dataType_dict_eval['body'].append('dict')
            necessaryFlag_dict = str(necessaryFlag_dict_eval).replace("'", '"')
            dataType_dict = str(dataType_dict_eval).replace("'", '"')
        if content_type == 'x-www-form-urlencoded':
            headers_eval['Content-Type'] = 'application/x-www-form-urlencoded'
        headers_eval = str(headers_eval).replace("'", '"')
        Api.objects.filter(api_id=api_id).update(api_name=api_name, api_path=api_path, method=method,
                                                 content_type=content_type, headers=headers_eval, body=body,
                                                 description=description, validate=validate, encry_flag=encry_flag,
                                                 relative_enc=encry_id, relative_pro=pro_id,
                                                 necessaryFlag_dict=necessaryFlag_dict, dataType_dict=dataType_dict,
                                                 description_dict=description_dict)
        return HttpResponseRedirect("/autoTest/api_index/")
    if request.method == 'GET':
        api_id = request.GET['api_id']
        api = Api.objects.get(api_id=api_id)
        cur_enc_id = api.relative_enc
        cur_pro_id = api.relative_pro
        cur_enc = Encryption.objects.get(encry_id=cur_enc_id)
        cur_pro = Project.objects.get(pro_id=cur_pro_id)
        pro_list = Project.objects.all()
        encry_list = Encryption.objects.all()
        return render(request, "autoTest/api_update.html", {"api": api,
                                                            "pro_list": pro_list,
                                                            "encry_list": encry_list,
                                                            "cur_enc": cur_enc,
                                                            "cur_pro": cur_pro,
                                                            })


def encry_index(request):
    encry_sum = Encryption.objects.all().order_by('encry_id')
    paginator = Paginator(encry_sum, 10)
    page = request.GET.get('page', 1)
    current_page = int(page)
    try:
        encry_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        encry_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        encry_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if encry_list.has_previous():
        previous_page_index = encry_list.previous_page_number()
    else:
        previous_page_index = None
    if encry_list.has_next():
        next_page_index = encry_list.next_page_number()
    else:
        next_page_index = None
    return render(request, 'autoTest/encry_index.html', context={'encry_list': encry_list,
                                                                 'paginator': paginator,
                                                                 'current_page': current_page,
                                                                 'previous_page_index': previous_page_index,
                                                                 'next_page_index': next_page_index
                                                                 })


def encry_add(request):
    if request.method == 'POST':
        encry_name = request.POST['encry_name']
        encry_function = request.POST['encry_function']
        description = request.POST['description']
        encry = Encryption(encry_name=encry_name, encry_function=encry_function, description=description)
        encry.save()
        return HttpResponseRedirect("/autoTest/encry_index/")
    if request.method == 'GET':
        return render(request, "autoTest/encry_add.html", {})



def encry_update(request):
    if request.method == 'POST':
        encry_id = request.POST['encry_id']
        encry_name = request.POST['encry_name']
        encry_function = request.POST['encry_function']
        description = request.POST['description']
        Encryption.objects.filter(encry_id=encry_id).update(encry_name=encry_name, encry_function=encry_function,
                                                            description=description)
        return HttpResponseRedirect("/autoTest/encry_index/")
    if request.method == 'GET':
        encry_id = request.GET['encry_id']
        encry = Encryption.objects.get(encry_id=encry_id)
        return render(request, 'autoTest/encry_update.html', context={"encry": encry})


def encry_delete(request):
    if request.method == 'GET':
        encry_id = request.GET['encry_id']
        Encryption.objects.filter(encry_id=encry_id).delete()
        return HttpResponseRedirect("/autoTest/encry_index/")


def testStep_index(request):
    page = request.GET.get('page', 1)
    pro_id = request.GET.get('pro_id', '')
    pro_sum = Project.objects.all()
    if pro_id:
        project = Project.objects.get(pro_id=pro_id)
        testStep_sum = TestStep.objects.filter(relative_pro=pro_id)
    else:
        project = None
        testStep_sum = TestStep.objects.all().order_by('testStep_id')
    paginator = Paginator(testStep_sum, 10)
    current_page = int(page)
    try:
        testStep_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        testStep_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        testStep_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if testStep_list.has_previous():
        previous_page_index = testStep_list.previous_page_number()
    else:
        previous_page_index = None
    if testStep_list.has_next():
        next_page_index = testStep_list.next_page_number()
    else:
        next_page_index = None
    return render(request, 'autoTest/testStep_index.html', context={'testStep_list': testStep_list,
                                                                    'paginator': paginator,
                                                                    'current_page': current_page,
                                                                    'previous_page_index': previous_page_index,
                                                                    'next_page_index': next_page_index,
                                                                    'pro_sum': pro_sum,
                                                                    'cur_pro': project,
                                                                    })


def testStep_add(request):
    if request.method == 'POST':
        testStep_name = request.POST['testStep_name']
        api_id = request.POST['api_id']
        pro_id = request.POST['pro_id']
        url = request.POST['url']
        skip = request.POST['skip']
        skipIf = request.POST['skipIf']
        skipUnless = request.POST['skipUnless']
        times = request.POST['times']
        method = request.POST['method']
        content_type = request.POST['content_type']
        description = request.POST['description']
        setup_hooks = request.POST['setup_hooks']
        teardown_hooks = request.POST['teardown_hooks']
        headers = request.POST['headers']
        body = request.POST['body']
        variables = request.POST['variables']
        validate = request.POST['validate']
        extract = request.POST['extract']
        necessaryFlag_dict = request.POST['necessaryFlag_dict']
        dataType_dict = request.POST['dataType_dict']
        description_dict = request.POST['description_dict']
        # 若不是以'['开头，']'结尾，则自动补充
        setup_hooks = goFunction.check_listFormat(setup_hooks)
        teardown_hooks = goFunction.check_listFormat(teardown_hooks)
        # 自动将中文括号（）转为英文括号()
        setup_hooks = goFunction.replace_chinese_brackets(setup_hooks)
        teardown_hooks = goFunction.replace_chinese_brackets(teardown_hooks)
        # 若content_type 为json或者x-www-form-urlencoded格式，自动添加请求头参数
        headers_eval = literal_eval(headers)
        if content_type == 'json':
            headers_eval['Content-Type'] = 'application/json'
            body = body.replace(' ', '')
            body_eval = literal_eval(body)
            dataType_dict_eval = literal_eval(dataType_dict)
            necessaryFlag_dict_eval = literal_eval(necessaryFlag_dict)
            for item in list(body_eval.values()):
                necessaryFlag_dict_eval['body'].append('1')
                if isinstance(item, str):
                    dataType_dict_eval['body'].append('string')
                if isinstance(item, int):
                    dataType_dict_eval['body'].append('int')
                if isinstance(item, float):
                    dataType_dict_eval['body'].append('double')
                if isinstance(item, list):
                    dataType_dict_eval['body'].append('list')
                if isinstance(item, dict):
                    dataType_dict_eval['body'].append('dict')
            necessaryFlag_dict = str(necessaryFlag_dict_eval).replace("'", '"')
            dataType_dict = str(dataType_dict_eval).replace("'", '"')
        if content_type == 'x-www-form-urlencoded':
            headers_eval['Content-Type'] = 'application/x-www-form-urlencoded'
        headers_eval = str(headers_eval).replace("'", '"')
        testStep = TestStep(testStep_name=testStep_name, skip=skip, skipIf=skipIf, skipUnless=skipUnless, times=times,
                            variables=variables, url=url, headers=headers_eval, method=method, content_type=content_type, body=body,
                            description=description, extract=extract, validate=validate, setup_hooks=setup_hooks,
                            teardown_hooks=teardown_hooks, relative_api=api_id, relative_pro=pro_id,
                            necessaryFlag_dict=necessaryFlag_dict, dataType_dict=dataType_dict,
                            description_dict=description_dict)
        testStep.save()
        return HttpResponseRedirect("/autoTest/testStep_index/")

    if request.method == 'GET':
        pro_list = Project.objects.all()
        return render(request, "autoTest/testStep_add.html", {
            'pro_list': pro_list,
        })


def testStep_update(request):
    if request.method == 'POST':
        testStep_id = request.POST['testStep_id']
        testStep_name = request.POST['testStep_name']
        api_id = request.POST['api_id']
        pro_id = request.POST['pro_id']
        url = request.POST['url']
        skip = request.POST['skip']
        skipIf = request.POST['skipIf']
        skipUnless = request.POST['skipUnless']
        times = request.POST['times']
        method = request.POST['method']
        content_type = request.POST['content_type']
        description = request.POST['description']
        setup_hooks = request.POST['setup_hooks']
        teardown_hooks = request.POST['teardown_hooks']
        headers = request.POST['headers']
        body = request.POST['body']
        variables = request.POST['variables']
        validate = request.POST['validate']
        extract = request.POST['extract']
        necessaryFlag_dict = request.POST['necessaryFlag_dict']
        dataType_dict = request.POST['dataType_dict']
        description_dict = request.POST['description_dict']
        # 若不是以'['开头，']'结尾，则自动补充
        setup_hooks = goFunction.check_listFormat(setup_hooks)
        teardown_hooks = goFunction.check_listFormat(teardown_hooks)
        # 自动将中文括号（）转为英文括号()
        setup_hooks = goFunction.replace_chinese_brackets(setup_hooks)
        teardown_hooks = goFunction.replace_chinese_brackets(teardown_hooks)
        # 若content_type 为json或者x-www-form-urlencoded格式，自动添加请求头参数
        headers_eval = literal_eval(headers)
        if content_type == 'json':
            headers_eval['Content-Type'] = 'application/json'
            body = body.replace(' ', '')
            body_eval = literal_eval(body)
            dataType_dict_eval = literal_eval(dataType_dict)
            necessaryFlag_dict_eval = literal_eval(necessaryFlag_dict)
            for item in list(body_eval.values()):
                necessaryFlag_dict_eval['body'].append('1')
                if isinstance(item, str):
                    dataType_dict_eval['body'].append('string')
                if isinstance(item, int):
                    dataType_dict_eval['body'].append('int')
                if isinstance(item, float):
                    dataType_dict_eval['body'].append('double')
                if isinstance(item, list):
                    dataType_dict_eval['body'].append('list')
                if isinstance(item, dict):
                    dataType_dict_eval['body'].append('dict')
            necessaryFlag_dict = str(necessaryFlag_dict_eval).replace("'", '"')
            dataType_dict = str(dataType_dict_eval).replace("'", '"')
        if content_type == 'x-www-form-urlencoded':
            headers_eval['Content-Type'] = 'application/x-www-form-urlencoded'
        headers_eval = str(headers_eval).replace("'", '"')
        TestStep.objects.filter(testStep_id=testStep_id).update(testStep_name=testStep_name, skip=skip, skipIf=skipIf,
                                                                skipUnless=skipUnless, times=times, variables=variables,
                                                                url=url, headers=headers_eval, method=method, content_type=content_type, body=body,
                                                                description=description, extract=extract,
                                                                validate=validate, setup_hooks=setup_hooks,
                                                                teardown_hooks=teardown_hooks, relative_api=api_id,
                                                                relative_pro=pro_id,
                                                                necessaryFlag_dict=necessaryFlag_dict,
                                                                dataType_dict=dataType_dict,
                                                                description_dict=description_dict)
        return HttpResponseRedirect("/autoTest/testStep_index/")
    if request.method == 'GET':
        pro_list = Project.objects.all()
        testStep_id = request.GET['testStep_id']
        testStep = TestStep.objects.get(testStep_id=testStep_id)
        cur_pro_id = testStep.relative_pro
        cur_api_id = testStep.relative_api
        cur_pro = Project.objects.get(pro_id=cur_pro_id)
        cur_api = Api.objects.get(api_id=cur_api_id)
        content_type = testStep.content_type
        jsonFlag = '0'
        if content_type == 'json':
            jsonFlag = '1'
        return render(request, "autoTest/testStep_update.html", {'testStep': testStep,
                                                                 'pro_list': pro_list,
                                                                 'cur_pro': cur_pro,
                                                                 'cur_api': cur_api,
                                                                 'jsonFlag': jsonFlag,
                                                                 })


def testStep_delete(request):
    if request.method == 'GET':
        testStep_id = request.GET['testStep_id']
        TestStep.objects.filter(testStep_id=testStep_id).delete()
        return HttpResponseRedirect("/autoTest/testStep_index/")


def testStep_run(request):
    if request.method == 'POST':
        testStep_id = request.POST.get('request_testStep_id','')
        testStep = TestStep.objects.get(testStep_id=testStep_id)
        url = request.POST.get('request_url','')
        headers = goFunction.changeHeadersFormat(testCasesObject=testStep, headerString=request.POST.get('request_headers', ''))
        body = goFunction.changeBodyFormat(testStepObject=testStep, bodyString=request.POST.get('request_body', ''))
        method = testStep.method.lower()
        content_type = testStep.content_type
        if method.lower() == 'get':
            response = requests.request(method=method, url=url, headers=headers, params=body)
        elif content_type == 'json':
            response = requests.request(method=method, url=url, headers=headers, json=body)
        else:
            response = requests.request(method=method, url=url, headers=headers, data=body)
        response_dict = {}
        response_dict['status_code'] = response.status_code
        response_dict['reason'] = goFunction.decodeChinese(response.reason)
        response_dict['headers'] = goFunction.decodeChinese(str(response.headers))
        response_dict['body'] = goFunction.decodeChinese(str(response.content))
        return JsonResponse(response_dict, safe=False)


def testCases_index(request):
    page = request.GET.get('page', 1)
    testCases_sum = TestCases.objects.all().order_by('testCases_id')
    paginator = Paginator(testCases_sum, 10)
    current_page = int(page)
    try:
        testCases_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        testCases_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        testCases_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if testCases_list.has_previous():
        previous_page_index = testCases_list.previous_page_number()
    else:
        previous_page_index = None
    if testCases_list.has_next():
        next_page_index = testCases_list.next_page_number()
    else:
        next_page_index = None
    return render(request, 'autoTest/testCases_index.html', context={'testCases_list': testCases_list,
                                                                     'paginator': paginator,
                                                                     'current_page': current_page,
                                                                     'previous_page_index': previous_page_index,
                                                                     'next_page_index': next_page_index
                                                                     })


def testCases_add(request):
    if request.method == 'POST':
        testCases_name = request.POST['testCases_name']
        testSuite_function = request.POST['testSuite_function']
        description = request.POST['description']
        setup_hooks = request.POST['setup_hooks']
        teardown_hooks = request.POST['teardown_hooks']
        headers = request.POST['headers']
        variables = request.POST['variables']
        parameters = request.POST['parameters']
        output = request.POST['output']
        testCases_list = request.POST['testCases_list']
        dataType_dict = request.POST['dataType_dict']
        description_dict = request.POST['description_dict']
        # parameters去掉'\'符号，替换双引号为单引号
        parameters = parameters.replace(r'\"',"'")
        # 若不是以'['开头，']'结尾，则自动补充
        setup_hooks = goFunction.check_listFormat(setup_hooks)
        teardown_hooks = goFunction.check_listFormat(teardown_hooks)
        output = goFunction.check_listFormat(output)
        setup_hooks = goFunction.replace_chinese_brackets(setup_hooks)
        teardown_hooks = goFunction.replace_chinese_brackets(teardown_hooks)
        headers = headers.replace("'", '"')
        dataType_dict = dataType_dict.replace("'", '"')
        if testSuite_function:
            # 去掉中文括号
            testSuite_function = goFunction.replace_chinese_brackets(testSuite_function)
        if not testSuite_function:
            testSuite_function = 'suiteFunction' + str(time.time())[:10] + '()'
        try:
            exist_testCases = TestCases.objects.get(testSuite_function=testSuite_function)
            print('testSuite_function用例集函数已存在 : ',exist_testCases.testSuite_function)
            testSuite_function = 'suiteFunction' + str(time.time())[:10] + '()'
            print('该用例集函数已自动命名为： ', testSuite_function)
        except:
            pass
        file_name = testCases_name + '_' + str(time.time())[:10] + '.json'
        file_path = os.path.join(hrun_base_dir, file_name)
        testCases = TestCases(testCases_name=testCases_name, testSuite_function=testSuite_function,
                              parameters=parameters, variables=variables, headers=headers, description=description,
                              setup_hooks=setup_hooks, teardown_hooks=teardown_hooks, output=output,
                              testCases_list=testCases_list, dataType_dict=dataType_dict,
                              description_dict=description_dict, file_path=file_path)
        testCases.save()
        # 创建 httprunner格式测试案例.json
        file_path = goFunction.createJsonFile(testCases)

        return HttpResponseRedirect("/autoTest/testCases_index/")
    if request.method == 'GET':
        # 测试步骤分页部分
        testStep_sum = TestStep.objects.all().order_by('testStep_id')
        testStep_list = []
        count = 0
        li_list = ''
        for testStep in testStep_sum:
            count = count + 1
            li = '<li name="testStep" value="' + str(testStep.testStep_id) + '">' + str(
                testStep.testStep_name) + r'</li>'
            li_list = li_list + li
            if str(count).endswith('0'):
                testStep_list.append(li_list)
                li_list = ''
            if count == len(testStep_sum):
                testStep_list.append(li_list)
        # 测试用例集分页部分
        testSuite_sum = TestCases.objects.all().order_by('testCases_id')
        testSuite_list = []
        count = 0
        li_list = ''
        for testCases in testSuite_sum:
            count = count + 1
            li = '<li name="testSuite" value="' + str(testCases.testCases_id) + '">' + str(
                testCases.testCases_name) + r'</li>'
            li_list = li_list + li
            if str(count).endswith('0'):
                testSuite_list.append(li_list)
                li_list = ''
            if count == len(testSuite_sum):
                testSuite_list.append(li_list)

        return render(request, "autoTest/testCases_add.html", {
            'testStep_list': testStep_list,
            'testSuite_list': testSuite_list,
        })



def testCases_update(request):
    if request.method == 'POST':
        testCases_id = request.POST['testCases_id']
        testCases_name = request.POST['testCases_name']
        testSuite_function = request.POST['testSuite_function']
        description = request.POST['description']
        setup_hooks = request.POST['setup_hooks']
        teardown_hooks = request.POST['teardown_hooks']
        headers = request.POST['headers']
        variables = request.POST['variables']
        parameters = request.POST['parameters']
        output = request.POST['output']
        testCases_list = request.POST['testCases_list']
        dataType_dict = request.POST['dataType_dict']
        description_dict = request.POST['description_dict']
        # parameters去掉'\'符号，替换双引号为单引号
        parameters = parameters.replace(r'\"', "'")
        # 若不是以'['开头，']'结尾，则自动补充
        setup_hooks = goFunction.check_listFormat(setup_hooks)
        teardown_hooks = goFunction.check_listFormat(teardown_hooks)
        output = goFunction.check_listFormat(output)
        setup_hooks = goFunction.replace_chinese_brackets(setup_hooks)
        teardown_hooks = goFunction.replace_chinese_brackets(teardown_hooks)
        headers = headers.replace("'", '"')
        dataType_dict = dataType_dict.replace("'", '"')
        if testSuite_function:
            # 去掉中文括号
            testSuite_function = goFunction.replace_chinese_brackets(testSuite_function)
        if not testSuite_function:
            testSuite_function = 'suiteFunction' + str(time.time())[:10] + '()'
        try:
            exist_testCases = TestCases.objects.get(testSuite_function=testSuite_function)
            print('testSuite_function用例集函数已存在 : ',exist_testCases.testSuite_function)
            testSuite_function = 'suiteFunction' + str(time.time())[:10] + '()'
            print('该用例集函数已自动命名为： ', testSuite_function)
        except:
            pass
        file_name = testCases_name + '_' + str(time.time())[:10] + '.json'
        file_path = os.path.join(hrun_base_dir, file_name)
        testCases = TestCases.objects.filter(testCases_id=testCases_id).update(testCases_name=testCases_name,
                                                                               testSuite_function=testSuite_function,
                                                                               parameters=parameters,
                                                                               variables=variables,
                                                                               headers=headers, description=description,
                                                                               setup_hooks=setup_hooks,
                                                                               teardown_hooks=teardown_hooks,
                                                                               output=output,
                                                                               testCases_list=testCases_list,
                                                                               dataType_dict=dataType_dict,
                                                                               description_dict=description_dict,file_path=file_path)
        # 创建 httprunner格式测试案例.json
        testCasesObject = TestCases.objects.get(testCases_id=testCases_id)
        file_path = goFunction.createJsonFile(testCasesObject)
        return HttpResponseRedirect("/autoTest/testCases_index/")
    if request.method == 'GET':
        # 测试步骤分页部分
        testStep_sum = TestStep.objects.all().order_by('testStep_id')
        testStep_list = []
        count = 0
        li_list = ''
        for testStep in testStep_sum:
            count = count + 1
            li = '<li name="testStep" value="' + str(testStep.testStep_id) + '">' + str(
                testStep.testStep_name) + r'</li>'
            li_list = li_list + li
            if str(count).endswith('0'):
                testStep_list.append(li_list)
                li_list = ''
            if count == len(testStep_sum):
                testStep_list.append(li_list)
        # 测试用例集分页部分
        testSuite_sum = TestCases.objects.all().order_by('testCases_id')
        testSuite_list = []
        count = 0
        li_list = ''
        for testCases in testSuite_sum:
            count = count + 1
            li = '<li name="testSuite" value="' + str(testCases.testCases_id) + '">' + str(
                testCases.testCases_name) + r'</li>'
            li_list = li_list + li
            if str(count).endswith('0'):
                testSuite_list.append(li_list)
                li_list = ''
            if count == len(testSuite_sum):
                testSuite_list.append(li_list)

        testCases_id = request.GET['testCases_id']
        testCases = TestCases.objects.get(testCases_id=testCases_id)
        testCases_list = []
        testCases_sum = literal_eval(testCases.testCases_list)
        for testStep_id in testCases_sum:
            testCases_list.append(TestStep.objects.get(testStep_id=testStep_id))

        return render(request, "autoTest/testCases_update.html", {'testStep_list': testStep_list,
                                                                  'testSuite_list': testSuite_list,
                                                                  'testCases': testCases,
                                                                  'testCases_list': testCases_list,
                                                                  })


def testCases_delete(request):
    if request.method == 'GET':
        testCases_id = request.GET['testCases_id']
        TestCases.objects.filter(testCases_id=testCases_id).delete()
        return HttpResponseRedirect("/autoTest/testCases_index/")


def testCases_run(request):
    '''
    request_runStyle: 
        "0": 不生成测试报告
        "1": 立即返回测试报告
        "2": 后台生成测试报告
        "3": 压力测试
    :return: 
    '''
    if request.method == 'POST':
        request_testCases_id = request.POST.get('request_testCases_id','')
        request_runStyle = request.POST.get('request_runStyle','')
        testCases = TestCases.objects.get(testCases_id=request_testCases_id)
        file_path = testCases.file_path
        testCases_name = testCases.testCases_name + '_report'
        if request_runStyle == '3':
            # 性能测试
            runner = HttpRunner(failfast=True, http_client_session=locust.client.Session())
            pass
        else:
            runner = HttpRunner(failfast=False)
        try:
            runner.run(file_path)
            summary = json.dumps(runner.summary['stat'])
        except:
            print('运行用例集报错!!')
        if request_runStyle == '0':
            # "0": 不生成测试报告
            return JsonResponse(summary, safe=False)
        if request_runStyle == '1':
            # "1": 立即返回测试报告
            report_path = runner.gen_html_report()
            report = Report(report_name=testCases_name, path=report_path, relative_testCases=request_testCases_id)
            report.save()
            report_id = str(Report.objects.filter(path=report_path)[0].report_id)
            redirect_url = r'http://127.0.0.1:8000/' + 'autoTest/report_show/?report_id=' + report_id
            return JsonResponse({'request_runStyle':'1', 'redirect_url': redirect_url}, safe=False)
        if request_runStyle == '2':
            # "2": 后台生成测试报告
            report_path = runner.gen_html_report()
            report = Report(report_name=testCases_name, path=report_path, relative_testCases=request_testCases_id)
            report.save()
            return JsonResponse(summary, safe=False)
        return HttpResponseRedirect("/autoTest/testCases_index/")


def report_index(request):
    report_sum = Report.objects.all().order_by('report_id')
    paginator = Paginator(report_sum, 10)
    page = request.GET.get('page', 1)
    current_page = int(page)
    try:
        report_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        report_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        report_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if report_list.has_previous():
        previous_page_index = report_list.previous_page_number()
    else:
        previous_page_index = None
    if report_list.has_next():
        next_page_index = report_list.next_page_number()
    else:
        next_page_index = None
    return render(request, 'autoTest/report_index.html', context={'report_list': report_list,
                                                                  'paginator': paginator,
                                                                  'current_page': current_page,
                                                                  'previous_page_index': previous_page_index,
                                                                  'next_page_index': next_page_index
                                                                  })

def report_show(request):
    if request.method == 'GET':
        report_id = request.GET['report_id']
        report_html_path = "autoTest/reports/" + Report.objects.get(report_id=report_id).path[-15:]
        return render(request, report_html_path,{ })

def report_delete(request):
    if request.method == 'GET':
        report_id = request.GET['report_id']
        file_path = Report.objects.get(report_id=report_id).path
        Report.objects.filter(report_id=report_id).delete()
        if (os.path.exists(file_path)):
            os.remove(file_path)
            print('成功删除测试报告文件： ', file_path)
        return HttpResponseRedirect("/autoTest/report_index/")


def plan_index(request):
    plan_sum = PeriodicTask.objects.all().order_by('id')
    paginator = Paginator(plan_sum, 10)
    page = request.GET.get('page', 1)
    current_page = int(page)
    try:
        plan_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        plan_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        plan_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if plan_list.has_previous():
        previous_page_index = plan_list.previous_page_number()
    else:
        previous_page_index = None
    if plan_list.has_next():
        next_page_index = plan_list.next_page_number()
    else:
        next_page_index = None

    # 映射时间配置
    intervalschedule_list = ['', ]
    for intervalschedule in IntervalSchedule.objects.all().order_by('id'):
        time_str = str(intervalschedule.every) + ' ' + intervalschedule.period
        intervalschedule_list.append(time_str)
        time_str = ''

    crontabschedule_list = ['', ]
    for crontabschedule in CrontabSchedule.objects.all().order_by('id'):
        time_str = str(crontabschedule.minute) + ' ' + str(crontabschedule.hour) + ' ' + str(
            crontabschedule.day_of_week) + ' ' + str(crontabschedule.day_of_month) + ' ' + str(
            crontabschedule.month_of_year) + '(m/h/d/dM/dY)'
        crontabschedule_list.append(time_str)
        time_str = ''

    return render(request, 'autoTest/plan_index.html', context={'plan_list': plan_list,
                                                               'paginator': paginator,
                                                               'current_page': current_page,
                                                               'previous_page_index': previous_page_index,
                                                               'next_page_index': next_page_index,
                                                               'intervalschedule_list': intervalschedule_list,
                                                                'crontabschedule_list': crontabschedule_list,
                                                               })

def getResponse(expect_response_content_type, expect_status_code, expect_headers, expect_response):
    '''
    根据mockServer保存的信息，返回特定的响应
    :param expect_response_content_type:  [json, text, xml, html]
    :param expect_status_code: 状态码
    :param expect_headers: 特定的响应头 为json字符串
    :param expect_response: 响应结果
    :return: response
    '''
    if expect_response_content_type == 'text':
        response = HttpResponse(expect_response)
        response.status_code = int(expect_status_code)
        if expect_headers:
            #  如果有请求头，则添加至响应头部里
            for key, value in json.loads(expect_headers):
                response[key] = value
        print('mock服务返回HttpResponse:', response)
        return response
    elif expect_response_content_type == 'json':
        json_data = json.loads(expect_response)
        response = JsonResponse(data=json_data, safe=False)
        response.status_code = int(expect_status_code)
        if expect_headers:
            #  如果有请求头，则添加至响应头部里
            for key, value in json.loads(expect_headers).items():
                response[key] = value
        print('mock服务返回JsonResponse:', response)
        return response
    elif expect_response_content_type == 'xml':
        raise Http404
    elif expect_response_content_type == 'html':
        raise Http404
    else:
        print(expect_response_content_type, ' not in [json, text, xml, html]')

def combine_response(return_mockServer):
    #  根据mockServer，生成并返回HttpResponse objects
    #如果请求参数条件匹配失败，给予默认响应
    setup_hooks = return_mockServer.setup_hooks
    teardown_hooks = return_mockServer.teardown_hooks
    expect_response_content_type = return_mockServer.expect_response_content_type
    expect_status_code = return_mockServer.expect_status_code
    expect_headers = return_mockServer.expect_headers
    expect_response = return_mockServer.expect_response
    if setup_hooks:
        #  在请求响应 产生前发生
        #  如果有setup函数，先执行setup函数
        #  暂时不做
        pass
    return_response = getResponse(
        expect_response_content_type=expect_response_content_type,
        expect_status_code=expect_status_code, expect_headers=expect_headers,
        expect_response=expect_response)
    if teardown_hooks:
        # 在请求响应 产生后发生
        #  如果有teardown函数，先执行teardown函数
        #  暂时不做
        pass
    return return_response  # 发送响应结果给客户端

def run_mock_server(request):
    # 跳转到mock服务
    request_uri = request.path
    if not request_uri.endswith(r'/'):
        request_uri = request_uri + r'/'
    mock_server_flag = Api.objects.filter(api_path=request_uri).filter(mock_status='1')
    if  mock_server_flag:
        #  如果存在mockServer配置，并且开关打开情况下，开始处理mock逻辑
        default_mockServer_id = Api.objects.filter(api_path=request_uri)[0].default_mockServer_id
        try:
            default_mockServer = MockServer.objects.get(mockServer_id=default_mockServer_id)  # 该接口的默认响应
            if default_mockServer.mock_status == '0':
                #  默认响应服务未开启
                default_mockServer = ''
        except ValueError:
            default_mockServer = ''
        worked_mockServer_suite = MockServer.objects.filter(uri=request_uri).filter(mock_status='1').order_by('mockServer_id')
        if worked_mockServer_suite:
            #  mockServer有开启服务的指定mock服务
            set_conditions_mockServer_suite = worked_mockServer_suite.exclude(conditions='')
            not_set_conditions_mockServer_suite = worked_mockServer_suite.filter(conditions='').order_by('mockServer_id')
            set_conditions_mockServer_suite_length = len(set_conditions_mockServer_suite)  #用于做最后一轮判断
            loop_index = 0  #用于做最后一轮判断
            if set_conditions_mockServer_suite:
                for set_conditions_mockServer in set_conditions_mockServer_suite:
                    #  e.g. conditions格式：[certId,contains,X,string,mockServerId]
                    loop_index = loop_index + 1
                    conditions =  set_conditions_mockServer.conditions.lstrip('[').rstrip(']').split(',')
                    if request.method == 'GET':
                        request_object = request.GET
                    else:
                        request_object = request.POST
                    try:
                        #  用于获取json格式的请求报文
                        request_json_data = json.loads(request.body)
                    except:
                        request_json_data = ''
                    if conditions[0] in request_object or conditions[0] in request_json_data:
                        #  如果数据库存的请求参数在实际发送的request里，
                        request_dict = request_object.dict()
                        if request_json_data:
                            check_value = request_json_data[conditions[0]]
                        else:
                            check_value = request_dict[conditions[0]]
                        #请求参数条件匹配判断
                        if goFunction.validate(check_value=check_value, comparator=conditions[1], expected_value=conditions[2], content_type=conditions[3]):
                            #如果请求参数条件匹配成功
                            return combine_response(set_conditions_mockServer)
                        else:
                            #  判断该循环是否是最后一个，如果是并且匹配失败，返回默认响应，否则跳过这次循环
                            if loop_index == set_conditions_mockServer_suite_length:
                                if default_mockServer:
                                    return combine_response(default_mockServer)
                                else:
                                    print('uri: ', request.path, '该接口没有设置默认响应！')
                                    raise Http404("您所访问的页面不存在！")
                            else:
                                continue
                    else:
                        #  数据库存的请求参数不在实际发送的request里，则跳过这次循环
                        #  判断该循环是否是最后一个，如果是并且匹配失败，返回默认响应，否则跳过这次循环
                        if loop_index == set_conditions_mockServer_suite_length:
                            if default_mockServer:
                                return combine_response(default_mockServer)
                            else:
                                print('uri: ', request.path, '该接口没有设置默认响应！')
                                raise Http404("您所访问的页面不存在！")
                        else:
                            continue
            else:
                if default_mockServer:
                    return combine_response(default_mockServer)
                else:
                    print('uri: ', request.path, '该接口没有设置默认响应！')
                    raise Http404("您所访问的页面不存在！")
        else:
            print('uri: ', request.path, '该mockServer服务尚未配置或者未开启服务！')
            raise Http404("您所访问的页面不存在！")
    else:
        print('uri: ', request.path, '该api-mock服务尚未配置或者未开启服务！')
        raise Http404("您所访问的页面不存在！")

def mockServer_index(request):
    # 筛选api列表sql：MockServer.objects.values('relative_api').distinct().order_by('relative_api')
    pro_sum = Project.objects.all()
    page = request.GET.get('page', 1)
    search_pro_id = request.GET.get('pro_id', '')
    search_uri = request.GET.get('uri', '')
    if search_pro_id and search_uri:
        project = Project.objects.get(pro_id=search_pro_id)
        api_sum = Api.objects.filter(relative_pro=search_pro_id).filter(api_path__contains=search_uri)
    elif search_pro_id and not search_uri:
        project = Project.objects.get(pro_id=search_pro_id)
        api_sum = Api.objects.filter(relative_pro=search_pro_id)
    elif not search_pro_id and search_uri:
        project = None
        api_sum = Api.objects.filter(api_path__contains=search_uri)
    else:
        project = None
        api_sum = Api.objects.all()
    paginator = Paginator(api_sum, 10)
    current_page = int(page)
    try:
        api_list = paginator.page(page)  # 获取当前页码的记录

        mockServer_select_list = []
        for api in api_list:
            #  生成当前页面api的mock响应下拉选项
            api_object = Api.objects.get(api_id=api.api_id)
            default_mockServer_id = api_object.default_mockServer_id
            # 筛选出条件为空的默认响应
            mockServer_suite = MockServer.objects.filter(relative_api=api.api_id).filter(conditions='')
            mockServer_loop_html = ''
            #  先填充默认选项放在第一位
            if default_mockServer_id:
                default_mockServer_name = MockServer.objects.get(mockServer_id=default_mockServer_id).mockServer_name
                default_option_html = r'<option value="{}">{}</option>'.format(default_mockServer_id,
                                                                               default_mockServer_name)
            else:
                default_option_html = r'<option value=""> </option>'
            mockServer_loop_html = mockServer_loop_html + default_option_html
            for mockServer in mockServer_suite:
                if str(mockServer.mockServer_id) != str(default_mockServer_id):
                    #  排出默认mockServer响应，防止重复
                    mockServer_loop_html = mockServer_loop_html + r'<option value="{}">{}</option>'.format(mockServer.mockServer_id, mockServer.mockServer_name)
            mockServer_loop_html = mockServer_loop_html + r'<option value=""> </option>'
            mockServer_select_list.append(mockServer_loop_html)
    except PageNotAnInteger:
        api_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容

    except EmptyPage:
        api_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    if api_list.has_previous():
        previous_page_index = api_list.previous_page_number()
    else:
        previous_page_index = None
    if api_list.has_next():
        next_page_index = api_list.next_page_number()
    else:
        next_page_index = None
    return render(request, 'autoTest/mockServer_index.html', context={'api_list': api_list,
                                                                       'paginator': paginator,
                                                                       'current_page': current_page,
                                                                       'previous_page_index': previous_page_index,
                                                                       'next_page_index': next_page_index,
                                                                       'pro_sum': pro_sum,
                                                                       'cur_pro': project,
                                                                       'search_uri': search_uri,
                                                                      'mockServer_select_list': mockServer_select_list,
                                                                    })

def mockServer_add(request):
    api_flag = request.POST.get('api_flag', '')
    mockServer_id = request.POST.get('mockServer_id', '')
    if request.method == 'GET':
        api_id = request.GET.get('api_id', '')
        pro_list = Project.objects.all()
        # mockServer_list = MockServer.objects.filter(relative_api=api_id)
        return render(request, 'autoTest/mockServer_add.html', context={'pro_list': pro_list,
                                                                       })
    #  保存单个mockServer响应
    if request.method == 'POST' and api_flag == 'save_single_mockServer':
        relative_api = request.POST.get('relative_api', '')
        setup_hooks = request.POST.get('setup_hooks', '')
        teardown_hooks = request.POST.get('teardown_hooks', '')
        mockServer_name = request.POST.get('mockServer_name', '')
        content_type = request.POST.get('content_type', '')
        status_code = request.POST.get('status_code', '')
        mockServer_headers = request.POST.get('mockServer_headers', '')
        #  headers数据库保存格式：e.g. ①json格式{'h1':'v1', 'h2':'v2'}
        mockServer_content = request.POST.get('mockServer_content', '')
        description = request.POST.get('description', '')
        mock_status = request.POST.get('mock_status', '1')
        api_object = Api.objects.get(api_id=relative_api)
        uri = api_object.api_path
        relative_pro =api_object.relative_pro
        if mockServer_id:
            mockServer = MockServer.objects.filter(mockServer_id=mockServer_id).update(mockServer_name=mockServer_name, uri=uri, relative_pro=relative_pro, relative_api=relative_api, setup_hooks=setup_hooks, teardown_hooks=teardown_hooks, expect_status_code=status_code, expect_headers=mockServer_headers, expect_response_content_type=content_type, expect_response=mockServer_content, mock_status=mock_status, description=description)
        else:
            mockServer = MockServer(mockServer_name=mockServer_name, uri=uri, relative_pro=relative_pro, relative_api=relative_api, setup_hooks=setup_hooks, teardown_hooks=teardown_hooks, expect_status_code=status_code, expect_headers=mockServer_headers, expect_response_content_type=content_type, expect_response=mockServer_content, mock_status=mock_status, description=description)
            mockServer.save()
            mockServer_id = mockServer.mockServer_id
        return JsonResponse({'mockServer_id':mockServer_id, 'mockServer_name':mockServer_name}, safe=False)
    # 保存单个mockServer匹配条件
    if request.method == 'POST' and api_flag == 'save_single_mockServer_condition':
        relative_api = request.POST.get('relative_api', '')
        mockServer_condition_arg = request.POST.get('mockServer_condition_arg', '')
        mockServer_condition_comparator = request.POST.get('mockServer_condition_comparator', '')
        mockServer_condition_expect_value = request.POST.get('mockServer_condition_expect_value', '')
        mockServer_condition_dataType = request.POST.get('mockServer_condition_dataType', '')
        mockServer_id = request.POST.get('mockServer_id', '')
        mockServer_condition_status_code = request.POST.get('mockServer_condition_status_code', '')
        conditions = '[{},{},{},{},{}]'.format(mockServer_condition_arg, mockServer_condition_comparator, mockServer_condition_expect_value, mockServer_condition_dataType, mockServer_condition_status_code)
        if mockServer_id:
            mockServer = MockServer.objects.filter(mockServer_id=mockServer_id).update(conditions=conditions)
            mockServer_name = MockServer.objects.get(mockServer_id=mockServer_id).mockServer_name
            return JsonResponse({'mockServer_id': mockServer_id, 'mockServer_name': mockServer_name}, safe=False)
        else:
            try:
                mockServer_object = MockServer.objects.get(mockServer_id=mockServer_condition_status_code)
                new_mockServer_object = MockServer(mockServer_name=mockServer_object.mockServer_name, uri=mockServer_object.uri, relative_pro=mockServer_object.relative_pro, relative_api=mockServer_object.relative_api, setup_hooks=mockServer_object.setup_hooks, teardown_hooks=mockServer_object.teardown_hooks, expect_status_code=mockServer_object.expect_status_code, expect_headers=mockServer_object.expect_headers, expect_response_content_type=mockServer_object.expect_response_content_type, expect_response=mockServer_object.expect_response, mock_status=mockServer_object.mock_status, description=mockServer_object.description)
                new_mockServer_object.save()
                new_mockServer_object_id = new_mockServer_object.mockServer_id
                MockServer.objects.filter(mockServer_id=new_mockServer_object_id).update(conditions=conditions)
                mockServer_name = MockServer.objects.get(mockServer_id=new_mockServer_object_id).mockServer_name
                return JsonResponse({'mockServer_id': new_mockServer_object_id, 'mockServer_name': mockServer_name}, safe=False)
            except Exception as e:
                print('新匹配响应条件保存失败, ', e)

def mockServer_update(request):
    if request.method == 'GET':
        api_id = request.GET.get('api_id','')
        cur_api = Api.objects.get(api_id=api_id)
        pro_list = Project.objects.all()
        api_list = Api.objects.filter(relative_pro=cur_api.relative_pro)
        cur_pro = Project.objects.get(pro_id=cur_api.relative_pro)
        default_mockServer_id = cur_api.default_mockServer_id
        if default_mockServer_id:
            default_mockServer = MockServer.objects.get(mockServer_id=default_mockServer_id)
        else:
            default_mockServer = ''
        return render(request, 'autoTest/mockServer_update.html', context={'pro_list': pro_list,
                                                                            'cur_pro': cur_pro,
                                                                            'cur_api': cur_api,
                                                                            'api_list': api_list,
                                                                           'default_mockServer': default_mockServer,
                                                                        })
    if request.method == 'POST':
        api_id = request.POST.get('api_id', '')
        api_flag = request.POST.get('api_flag', '')
        default_mockServer_id = request.POST.get('default_mockServer_id', '')
        if api_flag == 'save_default_mockServer':
            #  保存关联api的默认mockServer响应
            Api.objects.filter(api_id=api_id).update(default_mockServer_id=default_mockServer_id)
            return JsonResponse({'api_id':api_id},safe=False)

def mockServer_delete(request):
    if request.method == 'GET':
        api_id = request.GET.get('api_id', '')
        MockServer.objects.filter(relative_api=api_id).delete()
        return HttpResponseRedirect("/autoTest/mockServer_index/")


def find_data(request):
    model = request.POST.get('model', '')
    data_id = request.POST.get('data_id', '')
    data_name = request.POST.get('data_name', '')

    if model:
        if model.lower() == 'api':
            if data_id:
                data = Api.objects.filter(api_id=data_id).values()
                # print('--------------------',data,'-----------------------')
                return JsonResponse(list(data), safe=False)
        if model.lower() == 'pro':
            # 切换项目，获取接口列表
            if data_id and data_name == 'api_list':
                try:
                    # project = Project.objects.get(pro_id=data_id)
                    api_list = Api.objects.filter(relative_pro=data_id).values()
                    # print('--------------------', api_list, '-----------------------')
                except:
                    api_list = []
                return JsonResponse(list(api_list), safe=False)
            # 切换项目，获取环境列表
            if data_id and data_name == 'env_list':
                try:
                    # project = Project.objects.get(pro_id=data_id)
                    env_list = Environment.objects.filter(relative_pro=data_id).values()
                    print('----------env_list:  ', env_list)
                except:
                    env_list = []
                return JsonResponse(list(env_list), safe=False)
        if model.lower() == 'teststep':
            # 输入为空，则搜索全部
            if data_id == '' and data_name == 'testStep_list':
                testStep_sum = TestStep.objects.all().order_by('testStep_id')
                testStep_list = []
                count = 0
                li_list = ''
                for testStep in testStep_sum:
                    count = count + 1
                    li = '<li name="testStep" value="' + str(testStep.testStep_id) + '">' + str(
                        testStep.testStep_name) + r'</li>'
                    li_list = li_list + li
                    if str(count).endswith('0'):
                        testStep_list.append(li_list)
                        li_list = ''
                    if count == len(testStep_sum):
                        testStep_list.append(li_list)
                print('testStep_list: ', testStep_list)
                return JsonResponse(testStep_list, safe=False)
            if data_id and data_name == 'testStep_list':
                testStep1 = TestStep.objects.filter(testStep_name__contains=data_id)
                testStep2 = TestStep.objects.filter(url__contains=data_id)
                testStep_sum = testStep1 | testStep2
                testStep_list = []
                count = 0
                li_list = ''
                for testStep in testStep_sum:
                    count = count + 1
                    li = '<li name="testStep" value="' + str(testStep.testStep_id) + '">' + str(
                        testStep.testStep_name) + r'</li>'
                    li_list = li_list + li
                    if str(count).endswith('0'):
                        testStep_list.append(li_list)
                        li_list = ''
                    if count == len(testStep_sum):
                        testStep_list.append(li_list)
                print('testStep_list: ', testStep_list)
                return JsonResponse(testStep_list, safe=False)
            if data_id and data_name == 'testStep_dict':
                # 查找单个测试用例接口
                testStep_dict = { }
                try:
                    testStep = TestStep.objects.get(testStep_id=data_id)
                    testStep_dict['testStep_id'] = testStep.testStep_id
                    testStep_dict['url'] = testStep.url
                    testStep_dict['headers'] = testStep.headers
                    testStep_dict['body'] = testStep.body
                except:
                    testStep_dict = { }
                return JsonResponse(testStep_dict, safe=False)

        if model.lower() == 'testcases':
            if data_id == '' and data_name == 'testSuite_list':
                # 输入为空，则搜索全部
                testSuite_sum = TestCases.objects.all().order_by('testCases_id')
                testSuite_list = []
                count = 0
                li_list = ''
                for testSuite in testSuite_sum:
                    count = count + 1
                    li = '<li name="testSuite" value="' + str(testSuite.testCases_id) + '">' + str(
                        testSuite.testCases_name) + r'</li>'
                    li_list = li_list + li
                    if str(count).endswith('0'):
                        testSuite_list.append(li_list)
                        li_list = ''
                    if count == len(testSuite_sum):
                        testSuite_list.append(li_list)
                print('testSuite_list: ', testSuite_list)
                return JsonResponse(testSuite_list, safe=False)

            if data_id and data_name == 'testSuite_list':
                testSuite_sum = TestCases.objects.filter(testCases_name__contains=data_id)
                testSuite_list = []
                count = 0
                li_list = ''
                for testSuite in testSuite_sum:
                    count = count + 1
                    li = '<li name="testSuite" value="' + str(testSuite.testCases_id) + '">' + str(
                        testSuite.testCases_name) + r'</li>'
                    li_list = li_list + li
                    if str(count).endswith('0'):
                        testSuite_list.append(li_list)
                        li_list = ''
                    if count == len(testSuite_sum):
                        testSuite_list.append(li_list)
                print('testSuite_list: ', testSuite_list)
                return JsonResponse(testSuite_list, safe=False)
            if data_id and data_name == 'testStep_list':
                testStep_list = TestCases.objects.get(testCases_id=data_id).testCases_list
                # print(testStep_list)
                return JsonResponse(testStep_list, safe=False)
            if data_id and data_name == 'testCases_dict':
                # 运行测试用例集调用，获取单个测试用例集信息
                testCases_object = TestCases.objects.get(testCases_id=data_id)
                testCases_dict = { }
                testCases_dict['testCases_id'] = testCases_object.testCases_id
                testCases_dict['testCases_name'] = testCases_object.testCases_name
                testCases_dict['parameters'] = testCases_object.parameters
                testCases_dict['variables'] = testCases_object.variables
                testCases_list = testCases_object.testCases_list
                testStep_name_list_html = ''
                for testStep_id in literal_eval(testCases_list):
                    try:
                        temp_html = '<li>' + TestStep.objects.get(testStep_id=testStep_id).testStep_name + '</li>'
                        testStep_name_list_html = testStep_name_list_html + temp_html
                    except:
                        print('erroe occur!!')
                testStep_name_list_html = '<ul>' + testStep_name_list_html + "</ul>"
                testCases_dict['testStep_name_list_html'] = testStep_name_list_html
                return JsonResponse(testCases_dict, safe=False)
        if model.lower() == 'mockserver':
            if data_id and data_name == 'mockServer_content':
                api_object = Api.objects.get(api_id=data_id)
                # 只筛选出关联接口并且条件为空的默认mockServer
                mockServer_suite = MockServer.objects.filter(relative_api=api_object.api_id).filter(conditions='')
                default_mockServer_html = r'<option value=""></option>'
                default_mockServer_id = api_object.default_mockServer_id
                for mockServer in mockServer_suite:
                    if str(mockServer.mockServer_id) == str(default_mockServer_id):
                        default_mockServer_html = default_mockServer_html + r'<option value="{}"selected>{}</option>'.format(
                            mockServer.mockServer_id, mockServer.mockServer_name)
                    else:
                        default_mockServer_html = default_mockServer_html + r'<option value="{}">{}</option>'.format(
                            mockServer.mockServer_id, mockServer.mockServer_name)
                mockServer_suite = MockServer.objects.filter(relative_api=data_id)
                # 填充 响应集信息 的html代码
                mockServer_table_html = ''
                # 填充 匹配响应条件信息 的html代码
                mockServer_conditions_table_html = ''
                comparator_map = {'eq':'=', 'ge':'>=', 'lt':'<', 'le':'<=', 'len_eq': '长度等于', 'len_gt':'长度大于', 'len_lt':'长度小于', 'contains': '包含', 'contained_by':'被包含', 'startswith': 'startswith', 'endswith':'endswith'}
                try:
                    for mockServer_object in mockServer_suite:
                        row_1 = r'<td contenteditable="true" name="mockServer_name">{}</td>'.format(mockServer_object.mockServer_name)
                        row_2 = r'<td contenteditable="true" name="content_type"><select name="mockServer_row" class="form-control">'
                        content_type_list = ['json', 'text', 'xml', 'html']
                        temp_expect_response_content_type = mockServer_object.expect_response_content_type
                        for content_type in content_type_list:
                            if content_type == temp_expect_response_content_type:
                                temp_row_2_option = r'<option value="{}" selected> {} </option>'.format(content_type, content_type)
                                row_2 = row_2 + temp_row_2_option
                            else:
                                temp_row_2_option = r'<option value="{}"> {} </option>'.format(content_type, content_type)
                                row_2 = row_2 + temp_row_2_option
                        row_2 = row_2 + r'</select></td>'
                        row_3 = r'<td contenteditable="true" name="status_code"><select name="mockServer_row" class="form-control">'
                        status_code_list = ['200', '301', '302', '400', '403', '404', '405', '500', '502', '504']
                        temp_expect_status_code = mockServer_object.expect_status_code
                        for status_code in status_code_list:
                            if status_code == temp_expect_status_code:
                                temp_row_3_option = r'<option value="{}" selected> {} </option>'.format(status_code, status_code)
                                row_3 = row_3 + temp_row_3_option
                            else:
                                temp_row_3_option = r'<option value="{}"> {} </option>'.format(status_code, status_code)
                                row_3 = row_3 + temp_row_3_option
                        row_3 = row_3 + r'</select></td>'
                        row_4 = r'<td contenteditable="true" name="mockServer_headers">{}</td>'.format(mockServer_object.expect_headers)
                        row_5 = r'<td contenteditable="true" name="mockServer_content">{}</td>'.format(mockServer_object.expect_response)
                        row_6 = r'<td contenteditable="true" name="description">{}</td>'.format(mockServer_object.description)
                        if mockServer_object.mock_status == '0':
                            row_7 = r'<td><div class="bootstrap-switch-small bootstrap-switch bootstrap-switch-wrapper bootstrap-switch-animate bootstrap-switch-off" style="width: 60px;"><div class="bootstrap-switch-container" style="width: 94px; margin-left: -36px;"><span class="bootstrap-switch-handle-on bootstrap-switch-info" style="width: 40px;">ON</span><span class="bootstrap-switch-label" style="width: 40px;">&nbsp;</span><span class="bootstrap-switch-handle-off bootstrap-switch-danger" style="width: 40px;">OFF</span><input type="checkbox" name="switch" checked=""></div></div></td>'
                        else:
                            row_7 = r'<td><div class="bootstrap-switch-on bootstrap-switch-small bootstrap-switch bootstrap-switch-wrapper bootstrap-switch-animate" style="width: 60px;"><div class="bootstrap-switch-container" style="width: 94px; margin-left: 0px;"><span class="bootstrap-switch-handle-on bootstrap-switch-info" style="width: 40px;">ON</span><span class="bootstrap-switch-label" style="width: 40px;">&nbsp;</span><span class="bootstrap-switch-handle-off bootstrap-switch-danger" style="width: 40px;">OFF</span><input type="checkbox" name="switch" checked=""></div></div></td>'
                        row_8 = r'<td><button class="btn btn-success" onclick="save_mockServer_row(this)">保存</button><button class="btn btn-danger" onclick="del_row(this)">删除</button></td>'
                        temp_content = r'<tr name="mockServer-{}">'.format(mockServer_object.mockServer_id) + row_1 + row_2 + row_3 + row_4 + row_5 + row_6 + row_7 + row_8
                        mockServer_table_html = mockServer_table_html + temp_content

                        # 遍历生成 匹配响应条件信息
                        #格式如:(single_arg, validator,  expect_value, data_type, return_mockServer_id)
                        if mockServer_object.conditions:
                        #  如果响应匹配条件有值
                            conditions = mockServer_object.conditions.lstrip('[').rstrip(']').split(',')
                            try:
                                expect_args_list = literal_eval(api_object.body).keys()
                            except:
                                expect_args_list = [ ]
                            row_01 = r'<td contenteditable="true" name="request_args"><select class="form-control">'
                            for arg in expect_args_list:
                                if arg != conditions[0]:
                                    request_args_option = r'<option value="{}">{}</option>'.format(arg, arg)
                                    row_01 = row_01 + request_args_option
                                else:
                                    request_args_option = r'<option value="{}" selected>{}</option>'.format(arg, arg)
                                    row_01 = row_01 + request_args_option
                            row_01 = row_01 + r'</select></td>'
                            row_02 = r'<td><select name="comparator" class="form-control"><option value="{}">{}</option><option value="eq"> = </option><option value="gt"> &gt; </option><option value="ge"> &gt;= </option><option value="lt"> &lt; </option><option value="le"> &lt;= </option><option value="len_eq">长度等于</option><option value="len_gt">长度大于</option><option value="len_lt">长度小于</option><option value="contains">包含</option><option value="contained_by">被包含</option><option value="startswith">startswith</option><option value="endswith">endswith</option></select></td>'.format(conditions[1], comparator_map[conditions[1]])
                            row_03 = r'<td contenteditable="true" name="expect_value">{}</td>'.format(conditions[2])
                            row_04 = r'<td contenteditable="true" name="data_type"><select name="headers_data_type" class="form-control"><option value="{}" selected>{}</option><option value="string"> string </option><option value="int"> int </option><option value="double"> double </option><option value="list"> list </option><option value="dict"> dict </option></select></td>'.format(conditions[3], conditions[3])
                            row_05 = r'<td><select name="mockServer_select" class="form-control"><option value="{}" selected>{}</option>'.format(conditions[4], MockServer.objects.get(mockServer_id=conditions[4]).mockServer_name)
                            mockServer_suite = MockServer.objects.filter(relative_api=api_object.api_id)
                            for mockServer in mockServer_suite:
                                if str(mockServer.mockServer_id) != str(conditions[4]):
                                    row_05 = row_05 + r'<option value="{}">{}</option>'.format(mockServer.mockServer_id, mockServer.mockServer_name)
                            row_05 = row_05 + r'</select></td>'
                            row_06 = r'<td><button class="btn btn-success" onclick="save_mockServer_condition_row(this)">保存</button><button class="btn btn-danger" onclick="del_row(this)">删除</button></td>'
                            temp_content2 = r'<tr name="mockServer-{}">'.format(mockServer_object.mockServer_id) + row_01 + row_02 + row_03 + row_04 + row_05 + row_06 + '</tr>'
                            mockServer_conditions_table_html = mockServer_conditions_table_html + temp_content2
                    final_data = {'default_mockServer_html':default_mockServer_html, 'mockServer_table_html':mockServer_table_html, 'mockServer_conditions_table_html':mockServer_conditions_table_html}
                except Exception as e:
                    print('报错信息： ', e)
                    final_data = {'default_mockServer_html':default_mockServer_html, 'mockServer_table_html': '','mockServer_conditions_table_html': ''}

                return JsonResponse(final_data, safe=False)
            #  添加匹配响应条件行，获取接口请求参数列表
            if data_id and data_name == 'add_mockServer_condition':
                api_object = Api.objects.get(api_id=data_id)
                try:
                    expect_args_list = literal_eval(api_object.body).keys()
                except:
                    expect_args_list = []
                mockServer_default_condition_html = r'<td contenteditable="true" name="request_args"><select class="form-control"><option value=""></option>'
                for arg in expect_args_list:
                    mockServer_default_condition_html = mockServer_default_condition_html +  r'<option value="{}">{}</option>'.format(arg, arg)
                mockServer_default_condition_html = mockServer_default_condition_html + r'</select></td>'
                # 生成 返回响应select_html代码
                mockServer_suite = MockServer.objects.filter(relative_api=data_id)
                default_mockServer_id = Api.objects.get(api_id=data_id)
                mockServer_select_html = r'<select class="form-control" name="mockServer_select"><option value=""></option>'
                for mockServer in mockServer_suite:
                    if mockServer.mockServer_id == default_mockServer_id:
                        mockServer_select_html = mockServer_select_html + r'<option value="{}" selected>{}</option>'.format(mockServer.mockServer_id, mockServer.mockServer_name)
                    else:
                        mockServer_select_html = mockServer_select_html + r'<option value="{}">{}</option>'.format(mockServer.mockServer_id, mockServer.mockServer_name)
                mockServer_select_html = mockServer_select_html + r'</select>'
                return JsonResponse({'mockServer_default_condition_html':mockServer_default_condition_html, 'mockServer_select_html': mockServer_select_html}, safe=False)

            if data_id and data_name == 'mockServer_select':
                # 每次点击默认响应下拉框，更新最新的选项
                api_object = Api.objects.get(api_id=data_id)
                default_mockServer_id = api_object.default_mockServer_id
                mockServer_suite = MockServer.objects.filter(relative_api=data_id)
                mockServer_select_html = ''
                try:
                    for mockServer in mockServer_suite:
                        if mockServer.conditions == '':
                            # 只筛选出默认响应，条件响应不展示
                            if str(mockServer.mockServer_id) == str(default_mockServer_id):
                                mockServer_select_html = mockServer_select_html + r'<option value="{}">{}</option>'.format(mockServer.mockServer_id, mockServer.mockServer_name)
                            else:
                                mockServer_select_html = mockServer_select_html + r'<option value="{}">{}</option>'.format(mockServer.mockServer_id, mockServer.mockServer_name)
                    return JsonResponse({'mockServer_select_html': mockServer_select_html}, safe=False)
                except:
                    mockServer_select_html = r'<option value=""></option>'
                    return JsonResponse({'mockServer_select_html':mockServer_select_html}, safe=False)
