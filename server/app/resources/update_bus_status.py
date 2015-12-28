# -*- coding: utf-8 -*-
from __future__ import division
from server.app.extensions import auth, bcrypt
from flask_restful import Resource
from flask import request, jsonify
from server.app.models.bus import Bus
from flask_restful import fields
import os
import websocket
from uuid import uuid4
import time
import json
import threading
from server.app.config import LORIOT_WEBSOCKET_URL as ws_url
from redis import StrictRedis
from server.app.config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, LORIOT_PROTOCOL
from threading import Thread
# from server.app.utils.tools import timeout
import copy
import gevent
from gevent import Timeout

temp_euis = []
PACKET_SIZE = 48
TIME_OUT = 3600
redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
if not redis_conn.ping():
    raise Exception('redis没连接')


class UpdateBusStatus(Resource):

    # TODO:文件接收
    def get(self):
        timer = Timeout(30)
        timer.start()
        temp_euis = []
        euis = []
        try:
            buses = Bus.get_bus_list()
            euis = [b.eui for b in buses]

            global redis_conn
            pub = redis_conn.pubsub()
            ws = _connect_socket(ws_url)
            filter_euis(euis, ws, pub)

        except Timeout:
            return


def _connect_socket(ws_url):
    """
    创建 websocket 连接
    :param ws_url:websocket URL
    :return: 一个连接上了的ws
    """
    try:
        ws = websocket.WebSocket()
        ws.connect(url=ws_url)
        return ws
    except Exception:
        _connect_socket(ws_url)


def wrap_data(data, eui, index, end=False, port='1'):
    # 包装将要发送的数据
    # index需要加1，以确保板子收到的是正确的序号
    index += 1
    send_data = {"cmd": "tx", "EUI": "", "port": '1', "data": ""}
    send_data['EUI'] = eui
    send_data['port'] = port
    data_head = index | 0x00
    if end:
        data_head = index | 0x80

    data_head = '{0:02x}'.format(data_head)
    send_data['data'] = data_head + data.encode('hex')
    return json.dumps(send_data)


def init_euis(euis, ws):
    """
    发送检验数据
    :param euis: eui列表
    :param ws: websocket 连接
    :return:
    """
    for eui in euis:
        send_data = wrap_data('212342', eui, index=127, end=False)
        ws.send(send_data)


def get_index(data):
    """
    :param data:收到的信息
    :return: 信息中的序号
    """
    return int(data[2:4], 16)


def filter_euis(euis, ws, pubsub):
    """
    筛选不存在的eui
    :param euis: 要发送的eui列表
    :return: 有效的eui列表
    """
    global temp_euis

    init_euis(euis, ws)
    while True:
        for item in pubsub.listen():
            if not isinstance(item['data'], basestring):
                    continue
            recv_data = item['data']
            recv_data = json.loads(recv_data)

            if recv_data.get('h'):
                continue
            eui = recv_data.get('EUI')
            if eui in euis and recv_data.get('data', None):
                data = recv_data['data']

                if data[:2] == 'a1' or data[:2] == 'A1':
                    index = get_index(data)
                    if index == 0:
                        if eui not in temp_euis:
                            temp_euis.append(eui)
                        if len(euis) == len(temp_euis):
                            print '过滤完成'
                            break
        break


if __name__ == '__main__':
    import gevent
    from gevent import Timeout
    timeout = Timeout(5)
    timeout.start()

    def wait(seconds):
        gevent.sleep(seconds)
    try:
        gevent.spawn(wait, 2).join()
        print('Complete')
    except Timeout:
        print 'Could not complete'