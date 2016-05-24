# -*- coding: utf-8 -*-
from __future__ import division
import time
from greenlet import greenlet
from server.app.utils import MSocketIO, EventNameSpace
from server.app.config import OURSELF_APP_EUI, OURSELF_TOKEN, OURSELF_HOST, OURSELF_PORT
from gevent import Timeout
from binascii import unhexlify, hexlify
import json
LORA_HOST = OURSELF_HOST
APP_EUI = OURSELF_APP_EUI
TOKEN = OURSELF_TOKEN
LORA_PORT = OURSELF_PORT
NAMESPACE = '/test'

import logging


class TimeOutException(Exception):
    pass


class SendGroupManager(object):

    def __init__(self, content, group_eui, dev_euis, package_length=48, wait_time=10):
        self.content = content
        self.group_eui = group_eui
        self.dev_euis = dev_euis
        self._count = 0                                 # 丢失包的设备数
        self._uncompleted_devs = set()                  # device eui uncompleted
        self.failed_devs = list()                       # 发送失败的设备
        self.device_send_failed_flag = {}               # 单播时设备标志，标志刚发送的包是否失败
        self.socketio_cli = MSocketIO(LORA_HOST, LORA_PORT, EventNameSpace, params={'app_eui': APP_EUI, 'token': TOKEN})
        self.namespace = self.socketio_cli.define(EventNameSpace, path=NAMESPACE)
        self.package_length = package_length
        self.wait_time = wait_time
        self.content = []
        self.namespace.on('post_rx', self.on_post_rx)
        for i in range(int(len(content) / package_length) + 1):
            try:
                start = i * package_length
                end = (i + 1) * package_length
                self.content.append(content[start: end])
            except IndexError as e:
                self.content.append(content[i * package_length: ])

    def send(self):
        logging.info('Sending...')
        for i in range(len(self.content)):
            frament = self._wrap_data(self.content[i], i+1)
            logging.info('Sedding group message %s' % frament)
            self.namespace.emit('tx', frament)

            # 等待一定的时间，如果每个设备都接收成功，则继续往下发，否则继续等待，知道未成功的设备处理完毕
            logging.info('waiting...')
            self.socketio_cli.wait(self.wait_time)
            while self._uncompleted_devs:
                self.socketio_cli.wait(self.wait_time)
        # 终止信号
        end_frament = self._wrap_data('', len(self.content), mtx_flag=True)
        self.namespace.emit('tx', end_frament)
        logging.info('Success!')
        self.socketio_cli.disconnect()

    def single_send(self, eui, start, end):
        """
        发送单播数据, 发送完一个包后，等待接收，如果没接收到响应，继续发送，重复3次，如果仍未响应，则认为该设备当前不可接收，剔除该设备
        :param eui: 设备eui
        :param start: 开始的包索引
        :param end: 结束的包索引
        :return:
        """
        for i in range(start, end):
            if eui in self._uncompleted_devs:
                count = 0
                frament = self._wrap_single_data(eui.upper(), self.content[i], i+1)
                logging.info('Sending single message %s' % frament)
                self.namespace.emit('tx', frament)
                self.device_send_failed_flag[eui] = True        # 默认发送失败，只有发送成功时，才标志位False
                self.socketio_cli.wait(self.wait_time)
                while self.device_send_failed_flag.get(eui):
                    # 重新发送 3 次，如果还是失败，则把该设备删除排除在外
                    if count > 3:
                        count += 1
                        self.namespace.emit('tx', frament)
                        self.socketio_cli.wait(self.wait_time)
                    else:
                        # todo: 删除设备, 并且从_uncompleted_devs删除
                        try:
                            logging.info('remove device %s' % eui)
                            self.dev_euis.remove(eui)
                            self._uncompleted_devs.remove(eui)
                            self.failed_devs.append(eui)
                        except ValueError:
                            pass
                        break
        # 终止信号
        end_frament = self._wrap_single_data(eui, '', 1, tx_flag=True)
        self.namespace.emit('tx', end_frament)
        self._uncompleted_devs.remove(eui)

    def on_post_rx(self, data):
        if data['EUI'].upper() in map(lambda d: d.upper(), self.dev_euis):
            payload = data['data']
            if payload[:2] == 'A1':
                # 发送失败
                if int(payload[2:4], 16) - int(payload[4:6], 16) > 1:
                    self._continue = False
                    self._count += 1
                    self._uncompleted_devs.add(data['EUI'])
                    if not payload[6:8]:
                        self.single_send(data['EUI'], int(payload[2:4], 16), int(payload[4, 6], 16) - 1)
                else:
                    # 发送成功
                    self._count -= 1
                    self.device_send_failed_flag[data['EUI']] = False

    def _format_data(self, data, index, mtx_flag=False, tx_flag=False):
        """
        命令 | 当前序号 | 数据长度 | 数据
        --- |--- | --- | ---
        0xA0 | 0xXX | [7]stop, [6]end, [5:0]数据长度 | N * 0xXX
        >stop: 重发终止标志(1:结束)
        >end : 广播终止标志(1:结束)
        :param data:
        :return:
        """
        index_fmt = 0xA0 << 8 | index << 4
        length_fmt = mtx_flag << 7 | tx_flag << 6 | index
        res = (chr(index_fmt) + chr(length_fmt) + data).encode('hex')
        return res

    def _wrap_data(self, data, index, mtx_flag=False):
        # 包裹组播数据
        return json.dumps({
                    'cmd': 'mtx',
                    'EUI': self.group_eui,
                    'port': 3,
                    'data': self._format_data(data, index, mtx_flag=mtx_flag, tx_flag=False)
                })

    def _wrap_single_data(self, eui, data, index, tx_flag=False):
        # 包裹单个数据格式
        return json.dumps({
                    'cmd': 'tx',
                    'EUI': eui,
                    'port': 3,
                    'data': self._format_data(data, index, tx_flag=tx_flag, mtx_flag=False)
                })

if __name__ == '__main__':
    group_eui = '0000734E'
    dev_euis = ['0000000000000001']
    with open('3HelloNIOT.TXT', 'r') as f:
        logging.info('reading file ...')
        content = f.read()
        start = time.time()
        send_manager = SendGroupManager(content, group_eui, dev_euis, package_length=40)
        send_manager.send()
        end = time.time()
        print('Use %s seconds' %(end - start))