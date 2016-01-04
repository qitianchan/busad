# -*- coding:utf-8 -*-

from flask_restful import Resource
from redis import StrictRedis
from server.app.config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, LORIOT_PROTOCOL
from server.app.extensions import auth
from flask import g
redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
if not redis_conn.ping():
    raise Exception('redis没连接')


class AbortPublish(Resource):
    decorators = [auth.login_required]

    def get(self):
        progress_code = g.user.progress_code
        set_stop(redis_conn, progress_code)
        return '', 201

def set_stop(r, progress_code):
    progress_code_stop = progress_code + '.stop'

    r.set(progress_code_stop, 1)
    r.expire(progress_code_stop, 3600)
