testGo
======

python3.6.3 + bootstrap + jquery + js + httprunner

部署：
======
    mysql安装教程：https://www.cnblogs.com/wishwzp/p/7113403.html
    nginx + uWSGI搭建: https://blog.csdn.net/c465869935/article/details/53242126
    启动服务: sh deploy.sh
    启动beat若报错： ERROR: Pidfile (celerybeat.pid) already exists
    删掉项目下的celerybeat.pid文件即可

celery相关
======
    http://docs.celeryproject.org/en/latest/
    http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-naming-relative-imports
    celery worker/beat 后台启动(只支持python2): https://blog.csdn.net/qq_18863573/article/details/52437689

文件路径汇总：
======
    工程路径:                  /app/testGo
    工程静态文件路径:            /app/testGo/testGo/static
    wsgi.py的路径:             /app/testGo/testGo/wsgi.py
    uwsgi.ini的路径:           /app/testGo/testGo.ini
    uwsgi日志路径:             /app/testGo/uwsgi.log
    testGo.conf的路径:        /app/testGo/testGo.conf
    uwsgi_params的路径:        /app/nginx-1.6.2/conf/uwsgi_params
    nginx访问日志路径:          /app/testGo/logs/nginx.access.log
    nginx错误日志路径:          /app/testGo/logs/nginx.error.log

项目展示：
=====
![avatar](/static/img/index.png)
![avatar](/static/img/testStep_index.png)
![avatar](/static/img/testStep_run.png)
![avatar](/static/img/testCases_run.png)
![avatar](/static/img/report.png)
![avatar](/static/img/plan_index.png)
![avatar](/static/img/mockServer_index.png)
![avatar](/static/img/mockServer_update.png)
源码修改备注
======
    \testGo\manager.py
    <!--line4:-->
    from gevent import monkey
    <!--line7-->
        monkey.patch_all()

    \httprunner\init.py
    <!--注释以下代码-->
    # try:
    #     # monkey patch at beginning to avoid RecursionError when running locust.
    #     from gevent import monkey; monkey.patch_all()
    # except ImportError:
    #     pass

    \httprunner\report.py  line97-99
    # report_dir_path = os.path.join(os.getcwd(), "reports")
    # 修改保存报告的路径为\testGo\httprunner\tests\testcases\reports
    import platform
    # 兼容不同平台
    if platform.system() == 'Windows':
        report_dir_path = os.path.join(os.getcwd(), 'autoTest', 'templates', 'autoTest', 'reports')
    elif platform.system() == 'Linux':
        report_dir_path = os.path.join(os.getcwd(), 'autoTest', 'templates', 'autoTest', 'reports')
    else:
        pass


