# -*- coding:utf-8 -*-
# import djcelery
#
# djcelery.setup_loader()

broker_url  = 'redis://guest@172.30.3.60:6379//'
result_backend  = 'redis://guest@172.30.3.60:6379'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Shanghai'
enable_utc = True
# imports = (
#     'autoTest.tasks',
# )