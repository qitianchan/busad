# -*- coding: utf-8 -*-
from redis import StrictRedis
from server.app.config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
HOST = REDIS_HOST
PORT = REDIS_PORT
DB = REDIS_DB
from server.app.config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, \
    LORIOT_PROTOCOL, OURSELF_APP_EUI, OURSELF_TOKEN , OURSELF_HOST, OURSELF_PORT, NAMESPACE_PATH
from threading import Thread
from server.app.utils.tools import timeout
import copy
from socketIO_client import SocketIO, BaseNamespace
from logging import getLogger

# logger = getLogger()
# logger.setLevel('DEBUG')

LORA_HOST = OURSELF_HOST
APP_EUI = OURSELF_APP_EUI
TOKEN = OURSELF_TOKEN
LORA_PORT = OURSELF_PORT
NAMESPACE = NAMESPACE_PATH

strict_redis = StrictRedis(host=HOST, port=PORT, db=DB, password=REDIS_PASSWORD)

class EventNameSpace(BaseNamespace):

    def __init__(self, io, path=NAMESPACE):
        super(EventNameSpace, self).__init__(io, path)

    def on_connect(self):
        print('connected')


class MSocketIO(SocketIO):

    def __init__(self):
        super(MSocketIO, self).__init__(host=LORA_HOST, port=LORA_PORT,  params={'app_eui': APP_EUI, 'token': TOKEN})

    def define(self, Namespace, path=NAMESPACE_PATH):
        self._namespace_by_path[path] = namespace = Namespace(self, path)
        if path:
            self.connect(path)
        return namespace

# socketio_cli = MSocketIO(LORA_HOST, LORA_PORT, EventNameSpace, params={'app_eui': APP_EUI, 'token': TOKEN})
#
# event_space = socketio_cli.define(EventNameSpace, path=NAMESPACE)
if __name__ == '__main__':
    pass
