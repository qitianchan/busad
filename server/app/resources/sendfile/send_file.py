# -*- coding: utf-8 -*-
from __future__ import division
from server.app.extensions import auth, bcrypt
from flask_restful import Resource
from flask import request, jsonify
from server.app.models.user import User
from flask_restful import fields
import os
import websocket
from uuid import uuid4
import time
import json
import threading
from server.app.config import LORIOT_WEBSOCKET_URL as ws_url
from redis import StrictRedis
from server.app.config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, LORIOT_PROTOCOL, OURSELF_APP_EUI, OURSELF_TOKEN , OURSELF_HOST, OURSELF_PORT
from threading import Thread
from server.app.utils.tools import timeout
import copy
from socketIO_client import SocketIO, BaseNamespace
from greenlet import greenlet
from server.app.utils import MSocketIO, EventNameSpace
from server.app.config import OURSELF_APP_EUI, OURSELF_TOKEN, OURSELF_HOST, OURSELF_PORT
from gevent import Timeout

LORA_HOST = OURSELF_HOST
APP_EUI = OURSELF_APP_EUI
TOKEN = OURSELF_TOKEN
LORA_PORT = OURSELF_PORT
NAMESPACE = '/test'

socketio_cli = MSocketIO(LORA_HOST, LORA_PORT, EventNameSpace, params={'app_eui': APP_EUI, 'token': TOKEN})

event_space = socketio_cli.define(EventNameSpace, path=NAMESPACE)

class TimeOutException(Exception):
    pass


class SendGroupMessage(object):

    def __init__(self, content, group_eui, dev_euis, app_eui, token, namespace, socketio_cli, package_length=64, wait_time=10):
        self.content = content
        self.group_eui = group_eui
        self.app_eui = app_eui
        self.token = token
        self.dev_euis = dev_euis
        self.gl_send = greenlet(self.send)
        self._continue = True
        self._count = 0             # 丢失包的设备数
        self._uncompleted_devs = set()      # device eui uncompleted

        assert isinstance(namespace, 'EventNameSpace')
        self.namespace = namespace
        self.socketio_cli = socketio_cli
        self.package_length = package_length
        self.wait_time = wait_time
        self.content = []
        self.namespace.on('post_rx', self.on_post_rx)
        for i in range(content.length / package_length + 1):
            try:
                start = i * package_length
                end = (i + 1) * package_length
                self.content.append(content[start, end])
            except IndexError as e:
                self.content.append(content[i * package_length: ])

    def send(self):
        for i in range(len(self.content)):
            frament = self._wrap_data(self.content[i])
            self.namespace.emit('tx', frament)
            self.socketio_cli.wait(self.wait_time)
            while not self._continue or self._uncompleted_devs:
                self.socketio_cli.wait(self.wait_time)

    def single_send(self, eui, start, end):
        """
        发送单播数据
        :param eui: 设备eui
        :param start: 开始的包索引
        :param end: 结束的包索引
        :return:
        """
        for i in range(start, end):
            frament = self._wrap_single_data(self.content[i])
            self.namespace.emit('tx', frament)
            self.socketio_cli.wait(self.wait_time)
            while not self.devs_flag.get(eui):
                self.socketio_cli.wait(self.wait_time)

    def on_post_rx(self, data):
        if data['EUI'].upper() in map(lambda d: d.upper(), self.dev_euis):
            payload = data['data']
            if payload[:2] == 'A1':
                if payload[2:4] != '00':
                    self._continue = False
                    self._count += 1
                    self._uncompleted_devs.add(data['EUI'])
                else:
                    self._count -= 1
                    # try:
                    #     self._uncompleted_devs.remove(data['EUI'])
                    # except KeyError:
                    #     pass

    def _format_data(self):
        pass

    def _wrap_data(self, data):
        pass

if __name__ == '__main__':
    with Timeout(4):
        while True:
            print(time.ctime())
            time.sleep(1)