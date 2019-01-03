# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .celery import app
from autoTest.models import TestCases
import requests
import time

@app.task
def add(x, y):
    print('------**------- add function running...')
    time.sleep(2)
    print('--------**--------- add function finish.')
    return x + y


@app.task
def mul(x, y):
    print('------**------- mul function running...')
    time.sleep(2)
    print('--------**--------- mul function finish.')
    return x * y



@app.task
def run_testCases(testCases_id):
    url = r'http://localhost:8000/autoTest/testCases_run/'
    data = {'request_testCases_id':testCases_id, 'request_runStyle': '2'}
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    response = requests.post(url=url, data=data, headers=headers)
    print('*****  run_testCases-', testCases_id, ' task worked!')