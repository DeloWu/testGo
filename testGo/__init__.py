# from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app
from pymysql import install_as_MySQLdb
install_as_MySQLdb()


def mysqldb_escape(value, conv_dict):
    from pymysql.converters import encoders
    vtype = type(value)
    # note: you could provide a default:
    # PY2: encoder = encoders.get(vtype, escape_str)
    # PY3: encoder = encoders.get(vtype, escape_unicode)
    encoder = encoders.get(vtype, 'utf8')
    return encoder(value)

import pymysql
setattr(pymysql, 'escape', mysqldb_escape)
del pymysql
__all__ = ('celery_app',)