# -*- coding: utf-8 -*-
from __future__ import division
import logging
import time
from server.app.config import OURSELF_APP_EUI, OURSELF_TOKEN, OURSELF_HOST, OURSELF_PORT
LORA_HOST = OURSELF_HOST
APP_EUI = OURSELF_APP_EUI
TOKEN = OURSELF_TOKEN
LORA_PORT = OURSELF_PORT
NAMESPACE = '/test'

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)


class TimeOutException(Exception):
    pass


class GroupSender(object):

    def __init__(self, content, group_eui, dev_euis, package_length=20, wait_time=10, timeout=30):
        self.content = content
        self.group_eui = group_eui
        self.dev_euis = dev_euis
        self.time_out = 30
        # self._count = 0                                   # 丢失包的设备数
        self._uncompleted_devs = set()                      # device eui uncompleted,单播未完成的设备
        self._device_last_update_time = {}                  # 最后单播发送时间，用于判断这个设备是否还有用，每次单播发送时更新，整个单播过程完成时删除
        self.failed_devs = list()                           # 发送失败的设备
        # self.device_send_failed_flag = {}                 # 单播时设备标志，标志刚发送的包是否失败
        # self.socketio_cli = MSocketIO()
        self.package_length = package_length
        self.wait_time = wait_time
        self.content = []
        self.send_failed = False


        # self.namespace.on('connect', self.send)
        for i in range(int(len(content) / package_length) + 1):
            try:
                start = i * package_length
                end = (i + 1) * package_length
                self.content.append(content[start: end])
            except IndexError as e:
                self.content.append(content[i * package_length: ])

    def send(self):
            pass

    def single_send(self, eui, index, end=False):
        """
        发送单播数据, 发送完一个包后，等待接收，如果没接收到响应，继续发送，重复3次，如果仍未响应，则认为该设备当前不可接收，剔除该设备
        :param eui: 设备eui
        :param index:
        :return:
        """
        if not end and eui in self._uncompleted_devs:
            count = 0
            frament = self._wrap_single_data(eui.upper(), self.content[index-1], index)
            print('Sending single message %s' % frament)
            self.namespace.emit('tx', frament)
            self._device_last_update_time[eui] = time.time()
        else:
            # 终止信号
            end_frament = self._wrap_single_data(eui, '', 1, tx_flag=True)
            self.namespace.emit('tx', end_frament)
            try:
                self._uncompleted_devs.remove(eui)
            except KeyError:
                pass

            if eui in self._device_last_update_time:
                self._device_last_update_time.pop(eui)

    def on_post_rx(self, data):

        if data['EUI'].upper() in map(lambda d: d.upper(), self.dev_euis):
            payload = data['data']
            print('on_post_rx', data)
            if payload[:2] == 'A1':
                if payload[2:4] == '01':
                    self.is_broadcast_continue = True

                start_index = int(payload[4:6], 16)
                end_index = int(payload[6:8], 16)

                if int(end_index - start_index) > 1:
                    # 发送失败
                    # self._count += 1
                    self._uncompleted_devs.add(data['EUI'])
                    # if payload[2:4]:
                    self.single_send(data['EUI'], start_index + 1)
                else:
                    # 发送成功
                    # self._count -= 1
                    if payload[2:4] == '00':
                        self.single_send(data['EUI'], 1, end=True)

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
        length_fmt = tx_flag << 7 | mtx_flag << 6 | len(data)
        res = (chr(0xA0) + chr(index) + chr(length_fmt) + data).encode('hex')
        return res

    def _wrap_data(self, data, index, mtx_flag=False):
        # 包裹组播数据
        return {
                    'cmd': 'mtx',
                    'EUI': self.group_eui,
                    'port': 3,
                    'data': self._format_data(data, index, mtx_flag=mtx_flag, tx_flag=False)
                }

    def _wrap_single_data(self, eui, data, index, tx_flag=False):
        # 包裹单个数据格式
        return {
                    'cmd': 'tx',
                    'EUI': eui,
                    'port': 3,
                    'rx_window': 1,
                    'data': self._format_data(data, index, tx_flag=tx_flag, mtx_flag=False)
                }


class CommandSender(object):

    def __init__(self, eui, wait_time=10, send_group=False):
        self.eui = eui
        self.send_group = send_group
        self.cmd = 'tx' if not send_group else 'mtx'
        self.success = False
        self.wait_time = wait_time

    def on_connect(self):
        print('connect')

        self.send_message()

    def on_post_rx(self, data):
        print('on_post_rx', data)
        if data['EUI'].upper() == self.eui.upper():
            # todo something
            if data['data'][:2] == 'A1':
                print('receive message: ', data)
                self.success = True

    def send_message(self):
        pass


    def send(self):
        pass

    def _wrap_data(self):
        raise NotImplementedError


class OpenLightCommandSender(CommandSender):

    def _wrap_data(self):
        return {
                    'cmd': self.cmd,
                    'EUI': self.eui,
                    'port': 3,
                    'rx_window': 2,
                    'data': (chr(0xA2) + chr(0x50)).encode('hex')
                }


class CloseLightCommandSender(CommandSender):

    def _wrap_data(self):
        return {
                    'cmd': self.cmd,
                    'EUI': self.eui,
                    'port': 3,
                    'rx_window': 2,
                    'data': (chr(0xA2) + chr(0x51)).encode('hex')
                }


class RssiTestCommandSender(CommandSender):

    def _wrap_data(self):
        return {
                    'cmd': self.cmd,
                    'EUI': self.eui,
                    'port': 3,
                    'rx_window': 2,
                    'data': (chr(0xA2) + chr(0x52)).encode('hex')
                }


class UpLoadCommandSender(CommandSender):

    def _wrap_data(self):
        return {
                    'cmd': self.cmd,
                    'EUI': self.eui,
                    'port': 3,
                    'rx_window': 2,
                    'data': (chr(0xA2) + chr(0x53)).encode('hex')
                }


class UpLoadCommandSender_2(CommandSender):
    def _wrap_data(self):
        return {
                    'cmd': self.cmd,
                    'EUI': self.eui,
                    'port': 3,
                    'rx_window': 2,
                    'data': (chr(0xA2) + chr(0x54)).encode('hex')
                }


class UpLoadCommandSender_3(CommandSender):
    def _wrap_data(self):
        return {
                    'cmd': self.cmd,
                    'EUI': self.eui,
                    'port': 3,
                    'rx_window': 2,
                    'data': (chr(0xA2) + chr(0x55)).encode('hex')
                }


class UpLoadCommandSender_4(CommandSender):
    def _wrap_data(self):
        return {
                    'cmd': self.cmd,
                    'EUI': self.eui,
                    'port': 3,
                    'rx_window': 2,
                    'data': (chr(0xA2) + chr(0x56)).encode('hex')
                }


if __name__ == '__main__':
    group_eui = '0000734E'
    dev_euis = ['0000000000000002','0000000000000001']
    large_file = open('composer.lock', mode='r+')
    print(len(large_file.read()))
    with open('info2.TXT', 'rb') as f:
        print('reading file ...')
        content = f.read()

        start = time.time()
        send_manager = GroupSender(content, group_eui, dev_euis,wait_time=6, package_length=30)
        send_manager.send()
        end = time.time()
        print('Use %s seconds' % (end - start))


# if __name__ == '__main__':
#     from threading import Thread
#     import threading
#     import  time
#     thread_ids = []
#
#     class TestThread(Thread):
#         def run(self):
#             global thread_ids
#             thread_ids.append(self.ident)
#             try:
#                 while True:
#                     print(self.name, time.time())
#                     time.sleep(0.5)
#             finally:
#                 print(self.name, 'stop')
#
#
#     t1 = TestThread()
#     t2 = TestThread()
#     t1.start()
#     t2.start()
#     t1.join()
#     t2.join()
#     time.sleep(3)
#     thread_id = thread_ids[0]
#     thr = threading.

