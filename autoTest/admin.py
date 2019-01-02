from django.contrib import admin
from .models import Project,Environment,Api,TestStep,TestCases,Report

admin.site.register(Project)
admin.site.register(Environment)
admin.site.register(Api)
admin.site.register(TestStep)
admin.site.register(TestCases)
