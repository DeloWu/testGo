"""testGo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from autoTest import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'index/', views.index),
    path(r'', views.index),
    path(r'autoTest/', views.index),
    path(r'autoTest/', include('autoTest.urls')),
    re_path(r'.*/', views.run_mock_server, name='mock_server'),#用于跳转至mock服务
    path("favicon.ico", RedirectView.as_view(url=r'/static/img/yjsLogo.jpg')),
]

