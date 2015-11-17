# -*- coding: utf-8 -*-

import redis
from redis.exceptions import ConnectionError
import websocket
import json
from . import strict_redis
from server.app.config import LORIOT_WEBSOCKET_URL
import threading

# GATEWAY_ID = "be7a0029"
# TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"

# url = "wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN
url = LORIOT_WEBSOCKET_URL
r = strict_redis
ws = None


class Singleton(object):
    mutex = threading.Lock()                # 添加线程锁，保证线程安全

    def __new__(cls, *args, **kw):
        cls.mutex.acquire()
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        cls.mutex.release()
        return cls._instance


class Listening(Singleton):
    def __init__(self):
        ws = websocket.WebSocket()
        ws.connect(url)
        print 'ws 连接成功(Listening)'

    def ws_listening(self):
        res = r.ping()                  # 检测是否能够连接上 redis server
        print u'开始监听消息'

        # 一直连接直到连接成功
        try:
            # simulate(r)
            ws_app = websocket.WebSocketApp(url=url,
                                            on_message=on_message, on_open=on_open)

            ws_app.run_forever()
        except ConnectionError, e:
            print u'连接redis失败'
            raise ConnectionError('redis-server未启动')
        except Exception, e:
            # 连接不上是继续连接，递归调用
            self.ws_listening()


def ws_listening():
        res = r.ping()                  # 检测是否能够连接上 redis server
        print u'开始监听消息'

        # 一直连接直到连接成功
        try:
            # simulate(r)
            ws_app = websocket.WebSocketApp(url=url,
                                            on_message=on_message, on_open=on_open)

            ws_app.run_forever()
        except ConnectionError, e:
            print u'连接redis失败'
            raise ConnectionError('redis-server未启动')
        except Exception, e:
            # 连接不上是继续连接，递归调用
            ws_listening()

def wrap_listen():
    listen = Listening()
    listen.ws_listening()


def on_message(ws, message):
    eui = get_eui(message)
    print message
    if eui:
        try:
            r.publish(eui, message)
        except ConnectionError, e:
            print '连接redis失败'
            raise e

def on_open(wss):
    ws = wss
    print '连接websocket成功'


def get_eui(message):
    message = json.loads(message)
    eui = message.get('EUI', None)
    return eui


def publish_message(redis_conneted, eui, message):
    redis_conneted.publish(eui, message)


# 模拟发送消息
def simulate(redis_conn):
    from time import sleep
    i = 1
    while True:
        message = u'receive %s message' % i
        print message
        i += 1
        redis_conn.publish('hello', message)
        print u'发送消息成功'
        sleep(1)
