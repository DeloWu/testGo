# -*- coding:utf-8 -*-
from django import template

from autoTest.models import MockServer

#若使用自定义功能，template文件应该导入{% load generalfilters %}
register=template.Library()

@register.filter(name='get_name_from_id')
def get_name_from_id(value, modelName):
    pass

@register.simple_tag
def get_mockServer_select_options(api_id):
    pass