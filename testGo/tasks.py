# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .celery import app
from autoTest.models import TestCases
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
def xsum(numbers):
    return sum(numbers)

@app.task
def run_testCases(testCases_id):
    pass