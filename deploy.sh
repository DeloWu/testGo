#重启uwsgi
pkill -f uwsgi -9
uwsgi --ini /app/testGo/testGo.ini
#重启nginx
sh /app/nginx-1.6.2/bin/stop.sh
nginx -c /app/testGo/testGo.conf
