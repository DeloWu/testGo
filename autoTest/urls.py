# -*- coding:utf-8 -*-
from django.urls import path,re_path
from django.views.decorators.cache import cache_page
from . import views

app_name = 'autoTest'
urlpatterns = [
    path(r'index/', views.index),

    path(r'pro_index/', views.pro_index, name='pro_index'),
    path(r'pro_add/', views.pro_add, name='pro_add'),
    path(r'pro_update/', views.pro_update, name='pro_update'),
    path(r'pro_delete/', views.pro_delete, name='pro_delete'),

    path(r'env_index/', views.env_index, name='env_index'),
    path(r'env_add/', views.env_add, name='env_add'),
    path(r'env_update/', views.env_update, name='env_update'),
    path(r'env_delete/', views.env_delete, name='env_delete'),

    path(r'api_index/', views.api_index, name='api_index'),
    path(r'api_add/', views.api_add, name='api_add'),
    path(r'api_update/', views.api_update, name='api_update'),
    path(r'api_delete/', views.api_delete, name='api_delete'),

    path(r'encry_index/', views.encry_index, name='encry_index'),
    path(r'encry_add/', views.encry_add, name='encry_add'),
    path(r'encry_update/', views.encry_update, name='encry_update'),
    path(r'encry_delete/', views.encry_delete, name='encry_delete'),

    path(r'testStep_index/', views.testStep_index, name='testStep_index'),
    path(r'testStep_add/', views.testStep_add, name='testStep_add'),
    path(r'testStep_update/', views.testStep_update, name='testStep_update'),
    path(r'testStep_delete/', views.testStep_delete, name='testStep_delete'),
    path(r'testStep_run/', views.testStep_run, name='testStep_run'),
    
    path(r'testCases_index/', views.testCases_index, name='testCases_index'),
    path(r'testCases_add/', views.testCases_add, name='testCases_add'),
    path(r'testCases_update/', views.testCases_update, name='testCases_update'),
    path(r'testCases_delete/', views.testCases_delete, name='testCases_delete'),
    path(r'testCases_run/', views.testCases_run, name='testCases_run'),

    path(r'report_index/', views.report_index, name='report_index'),
    path(r'report_show/', views.report_show, name='report_show'),
    path(r'report_delete/', views.report_delete, name='report_delete'),

    path(r'plan_index/', views.plan_index, name='plan_index'),

    path(r'mockServer_index/', views.mockServer_index, name='mockServer_index'),
    path(r'mockServer_add/', views.mockServer_add, name='mockServer_add'),
    path(r'mockServer_update/', views.mockServer_update, name='mockServer_update'),
    path(r'mockServer_delete/', views.mockServer_delete, name='mockServer_delete'),
    
    path(r'find_data/', views.find_data, name='find_data'),

]
