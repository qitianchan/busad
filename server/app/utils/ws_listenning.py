# -*- coding: utf-8 -*-

import redis
from redis.exceptions import ConnectionError
import websocket
import json
from . import strict_redis


GATEWAY_ID = "be7a0029"
TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"

url = "wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN
r = strict_redis
ws = None

def ws_listenning():
    print u'开始监听消息'


    # 一直连接直到连接成功
    try:
        simulate(r)
        ws_app = websocket.WebSocketApp(url=url,
                                        on_message=on_message, on_open=on_open)

        ws_app.run_forever()
    except ConnectionError, e:
        raise e
    except Exception, e:
        # 连接不上是继续连接，递归调用
        ws_listenning()


def on_message(ws, message):
    eui = get_eui(message)
    if eui:
        r.publish(eui, message)
    print message


def on_open(ws):
    ws = ws

def get_eui(message):
    message = json.dumps(message)
    eui = message.get('eui', None)
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
