import django
from django.db import models
import django.utils.timezone as timezone
from datetime import datetime


class Project(models.Model):
    pro_id = models.AutoField(primary_key=True, null=False)
    pro_name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.pro_name

    __repr__ = __str__


class Environment(models.Model):
    env_id = models.AutoField(primary_key=True, null=False)
    env_name = models.CharField(max_length=20)
    # project = models.ForeignKey('Project', on_delete=models.CASCADE)
    relative_pro = models.CharField(max_length=10)
    description = models.CharField(max_length=100, blank=True, default="")
    url = models.CharField(max_length=100)
    port = models.CharField(max_length=10)

    def __str__(self):
        return self.env_name

    __repr__ = __str__


class Api(models.Model):
    api_id = models.AutoField(primary_key=True, null=False)
    api_name = models.CharField(max_length=20)  # api中文名称
    api_path = models.CharField(max_length=200)  # api请求路径(url) e.g. /api/v1/Account/Login
    method = models.CharField(max_length=10)  # 请求方式  e.g.  GET/POST/DELETE/HEAD
    headers = models.TextField(blank=True, default="{ }")  # 请求头,dict,包括报文体(Content-Type)、cookies、额外请求参数等
    content_type = models.CharField(max_length=50)  # 请求参数格式 ，e.g.  form-data/x-www-form-urlencoded/json/params
    body = models.TextField(blank=True, default="{ }")  # 请求体,dict, {"param1":"value1","param2":"value2"}
    description = models.CharField(max_length=200, blank=True, default="")  # api内容描述,参数描述
    '''
    校验器，list of dict , comparator: [ gt, ge, lt, le, len_eq, len_gt, len_lt, contains, contained_by, startswith, endswith ]
    e.g.
    [   { comparator: [ check_value, expect_value ] },
        { eq: [ 'status_code', 200 ] },
        { eq: [ 'content.IsSuccess', true ] },
        { eq: [ 'content.Code', 200 ] }
    ]
    '''
    validate = models.TextField(blank=True, default="[ ]")
    encry_flag = models.IntegerField(default=0)  # 0为不加密,1为加密
    necessaryFlag_dict = models.TextField(blank=True, default='{"headers":[], "body":[]}')
    dataType_dict = models.TextField(blank=True, default='{"headers":[], "body":[], "validate":[]}')
    description_dict = models.TextField(blank=True, default='{"headers":[], "body":[], "validate":[]}')
    relative_enc = models.CharField(max_length=10)
    relative_pro = models.CharField(max_length=10)
    # 配合mock服务字段
    mock_status = models.CharField(max_length=10, blank=True, default="False")   #'True' or 'False'
    default_mockServer_id = models.CharField(max_length=4, blank=True, default="")    #默认mock响应状态

    def __str__(self):
        return self.api_name

    __repr__ = __str__


class TestStep(models.Model):
    testStep_id = models.AutoField(primary_key=True, null=False)
    testStep_name = models.CharField(max_length=20)
    skip = models.CharField(max_length=10, blank=True, default="")  # 当Boolean使用
    skipIf = models.CharField(max_length=50, blank=True, default="")  # 执行函数  e.g. ${functionName(*args, **kwargs)}
    skipUnless = models.CharField(max_length=50, blank=True, default="")  # 执行函数  e.g. ${functionName(*args, **kwargs)}
    times = models.IntegerField(default=1)
    variables = models.TextField(blank=True, default="[ ]")  # list of dict,静态变量
    url = models.CharField(max_length=200)  # 请求url e.g. ①http://127.0.0.1/apiPath ②/apiPath ③$ip_port_variables/apiPath
    headers = models.TextField(blank=True, default="{ }")  # 请求头,dict,包括报文体(Content-Type)、cookies、额外请求参数等
    content_type = models.CharField(max_length=50)  # 请求参数格式 ，e.g.  form-data/x-www-form-urlencoded/json/params
    method = models.CharField(max_length=10)  # 请求方法  e.g.  GET/POST/DELETE/HEAD
    body = models.TextField(blank=True, default="{ }")  # 请求体,dict
    description = models.CharField(max_length=200, blank=True, default="")  # 测试步骤内容描述
    extract = models.TextField(blank=True, default="[ ]")  # 提取参数, list of dict, e.g. [ {"token": "content.token"} ]
    '''
       校验器，list of dict , comparator: [ gt, ge, lt, le, len_eq, len_gt, len_lt, contains, contained_by, startswith, endswith ]
       e.g.
       [   { comparator: [ check_value, expect_value ] },
           { eq: [ 'status_code', 200 ] },
           { eq: [ 'content.IsSuccess', true ] },
           { eq: [ 'content.Code', 200 ] }
       ]
       '''
    validate = models.TextField(blank=True, default="[ ]")
    '''
    钩子函数,
    setup_hooks: 在 HTTP 请求发送前执行 hook 函数，主要用于准备工作；也可以实现对请求的 request 内容进行预处理。
    teardown_hooks: 在 HTTP 请求发送后执行 hook 函数，主要用于测试后的清理工作；也可以实现对响应的 response 进行修改，例如进行加解密等处理。
    list ,e.g.
    [
        "${setup_hook_prepare_kwargs($request)}",
        "${setup_hook_httpntlmauth($request)}"
    ]
    '''
    setup_hooks = models.CharField(max_length=200, blank=True, default='[]')
    '''
    setup_hooks 函数放置于 debugtalk.py 中，并且必须包含三个参数：
    method: 请求方法，e.g. GET, POST, PUT
    url: 请求 URL
    kwargs: request 的参数字典
    '''
    teardown_hooks = models.CharField(max_length=200, blank=True, default='[]')
    '''
    teardown_hooks 函数放置于 debugtalk.py 中，并且必须包含一个参数：
    resp_obj: requests.Response 实例
    '''
    necessaryFlag_dict = models.TextField(blank=True, default='{"headers":[], "body":[], "variables":[]}')
    dataType_dict = models.TextField(blank=True, null=True, default='{"headers":[], "body":[], "validate":[], "variables":[]}')
    description_dict = models.TextField(blank=True, null=True, default='{"headers":[], "body":[], "validate":[], "variables":[]}')

    relative_api = models.CharField(max_length=10)
    relative_pro = models.CharField(max_length=10)

    def __str__(self):
        return self.testStep_name

    __repr__ = __str__


class TestCases(models.Model):
    testCases_id = models.AutoField(primary_key=True, null=False)
    testCases_name = models.CharField(max_length=20)
    testSuite_function = models.CharField(max_length=50,default="",
                                          blank=True)  # 若为testSuite，则config的"def"必填 e.g. "def": "testSuiteName2($page,$num)"
    '''
    全局参数，用于实现数据化驱动，作用域为整个用例
    list of dict e.g.
    [
        {"user_agent": ["iOS/10.1", "iOS/10.2", "iOS/10.3"]},
        {"app_version": "${P(app_version.csv)}"},
        {"os_platform": "${get_os_platform()}"}
    ]
    '''
    parameters = models.TextField(blank=True, default='[ ]')
    '''
    定义的全局变量，作用域为整个用例
    list of dict    e.g.
    [
        {"user_agent": "iOS/10.3"},
        {"device_sn": "${gen_random_string(15)}"},
        {"os_platform": "ios"}
    ]
    '''
    variables = models.TextField(blank=True, default='[ ]')
    headers = models.TextField(blank=True, default="{ }")  # 请求头,dict,包括报文体(Content-Type)、cookies、额外请求参数等
    description = models.CharField(max_length=200, blank=True, default="")  # 用例集内容描述
    '''
        testCases层的钩子函数,
        setup_hooks: 在整个用例开始执行前触发 hook 函数，主要用于准备工作。
        teardown_hooks: 在整个用例结束执行后触发 hook 函数，主要用于测试后的清理工作。
        list ,e.g.
        [
            "${setup_hook_prepare_kwargs($request)}",
            "${setup_hook_httpntlmauth($request)}"
        ]
        '''
    setup_hooks = models.CharField(max_length=200, blank=True, default='[]')
    '''
    setup_hooks 函数放置于 debugtalk.py 中，并且必须包含三个参数：
    method: 请求方法，e.g. GET, POST, PUT
    url: 请求 URL
    kwargs: request 的参数字典
    '''
    teardown_hooks = models.CharField(max_length=200, blank=True, default='[]')
    '''
    teardown_hooks 函数放置于 debugtalk.py 中，并且必须包含一个参数：
    resp_obj: requests.Response 实例
    '''
    output = models.CharField(max_length=150, blank=True, default='[]')
    '''
    list,整个用例输出的参数列表，可输出的参数包括公共的 variable 和 extract 的参数; 在 log-level 为 debug 模式下，会在 terminal 中打印出参数内容
    '''
    testCases_list = models.CharField(max_length=150)  # case_id集,list  e.g. [ 1001, 1002, 1003 ]
    dataType_dict = models.TextField(blank=True, default='{"headers":[], "parameters":[], "variables":[]}')
    description_dict = models.TextField(blank=True, default='{"headers":[], "parameters":[], "variables":[]}')
    file_path = models.CharField(max_length=150, blank=True, default="")

    def __str__(self):
        return self.testCases_name

    __repr__ = __str__


class Encryption(models.Model):
    encry_id = models.AutoField(primary_key=True, null=False)
    encry_name = models.CharField(max_length=20)  # 加密名称
    encry_function = models.CharField(max_length=200)  # 加密函数名称
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.encry_name

    __repr__ = __str__


class Report(models.Model):
    report_id = models.AutoField(primary_key=True, null=False)
    report_name = models.CharField(max_length=50)  # 报告文件名称
    path = models.CharField(max_length=100)  # 报告文件路径
    relative_testCases = models.CharField(max_length=10)
    create_time = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return self.report_name

    __repr__ = __str__


class MockServer(models.Model):
    # mock服务响应集
    mockServer_id = models.AutoField(primary_key=True, null=False)
    mockServer_name = models.CharField(max_length=20)    # mockServer响应名称
    uri = models.CharField(max_length=200)
    relative_pro = models.CharField(max_length=10)
    relative_api = models.CharField(max_length=10)
    setup_hooks = models.CharField(max_length=200, blank=True, default='[]')    #e.g. [func1(1,2,3);func2();func3(request);func4(response)]
    teardown_hooks = models.CharField(max_length=200, blank=True, default='[]')    #e.g. [func1(1,2,3);func2();func3(request);func4(response)]
    expect_status_code = models.IntegerField(default=200)    #响应状态码
    expect_headers = models.TextField(blank=True, default='')
    expect_response_content_type = models.CharField(max_length=10, blank=True, default='json')    #响应内容格式: json/text/html/xml
    expect_response = models.TextField(blank=True, default='')
    status = models.CharField(max_length=2, blank=True, default='1')   #mock服务是否打开: 0关, 1开
    conditions = models.TextField(blank=True, default='')    #e.g. [(args(data1.data2),validator,expect_value,return_mockServer_id)]
    description = models.CharField(max_length=100, blank=True, default="")
