from gevent import monkey
monkey.patch_all()
from celery import Celery
import os
import django
from celery.schedules import crontab
import platform

# 启动celery命令(\djangoProject\testGo路径下):
# celery -A testGo worker -l info -P gevent
# celery -A testGo beat -l info
# celery multi start/stop/stopwait w1 -A proj -l info
# celery -A testGo control add_consumer celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testGo.settings")
# django.setup()  会导致部署在linux环境执行manager.py报错

if platform.system() == 'Windows':
    app = Celery('testGo',
                 broker='redis://guest@47.112.22.9:6379//',
                 backend='redis://guest@47.112.22.9:6379',
                 include=['testGo.tasks'])

else:
    # 若部署在linux上，注释掉上面app代码并替换
    app = Celery('testGo',
                 broker='redis://guest@127.0.0.1:6379//',
                 backend='redis://guest@127.0.0.1:6379',
                 include=['testGo.tasks'])


# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
    timezone='Asia/Shanghai',
    # 配置定时器模块，定时器信息存储在数据库中
    beat_scheduler='django_celery_beat.schedulers.DatabaseScheduler',
)
'''
文档地址:  http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
启动定时任务做法
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )

@app.task
def test(arg):
    print(arg)
'''

if __name__ == '__main__':
    app.start()