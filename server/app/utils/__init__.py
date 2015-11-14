# -*- coding: utf-8 -*-
from redis import StrictRedis
from server.app.config import REDIS_DB, REDIS_HOST, REDIS_PORT
HOST = REDIS_HOST
PORT = REDIS_PORT
DB = REDIS_DB

strict_redis = StrictRedis(host=HOST, port=PORT, db=DB)
