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
import time


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
        print('connect')

class MSocketIO(SocketIO):

    def define(self, Namespace, path=''):
        self._namespace_by_path[path] = namespace = Namespace(self, path)
        if path:
            self.connect(path)
        return namespace



def on_ack_tx(data):
    print('data:', data)

if __name__ == '__main__':
    socketio_cli = MSocketIO(LORA_HOST, LORA_PORT, params={'app_eui': APP_EUI, 'token': TOKEN})

    event_space = socketio_cli.define(EventNameSpace, path=NAMESPACE)

    event_space.on('ack_tx', on_ack_tx)
    while True:
        if socketio_cli.connected:
            print('send...')
            event_space.emit('tx', {
                                'cmd': 'tx',
                                'EUI': '0000000000000002',
                                'port': 3,
                                'data': 'what the fuck'.encode('hex')
                            })
            socketio_cli.wait(5)
