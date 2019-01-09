#重启celery worker和beat
killall celery
nohup celery -A testGo worker -l info -P gevent >/dev/null 2>&1 &
#重启celery worker和beat
killall celery
nohup celery -A testGo worker -l info -P gevent >/dev/null 2>&1 &
nohup celery -A testGo beat -l info >/dev/null 2>&1 &

#重启uwsgi
pkill -f uwsgi -9
uwsgi --ini /app/testGo/testGo.ini
#重启nginx
sh /app/nginx-1.6.2/bin/stop.sh
nginx -c /app/testGo/testGo.conf