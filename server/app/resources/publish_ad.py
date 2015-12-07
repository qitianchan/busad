# -*- coding: utf-8 -*-
from __future__ import division
from server.app.extensions import auth, bcrypt
from flask_restful import Resource
from flask import request, jsonify, g
from flask_restful import fields
import os
import websocket
from uuid import uuid4
import time
import json
import threading
from server.app.utils import strict_redis
from server.app.config import LORIOT_WEBSOCKET_URL as ws_url
from redis import StrictRedis
from server.app.config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, LORIOT_PROTOCOL
from datetime import datetime
from server.app.utils.tools import timelimit
from server.app.utils.ws_listenning import ws_app


PACKET_SIZE = 15
TIME_OUT = 3600
# r = strict_redis


class Publish(Resource):

    # TODO:文件接收
    def post(self):
        f = request.files['file']

        euis = request.form.get('euis')
        if euis:
            euis = euis.split(',')
            ws = None
            # if ws == None:
            #     ws = _connet_socket(ws_url)
            chunks = slipe_file(f, PACKET_SIZE)
            process_code = uuid4().hex

            new_thread = threading.Thread(target=send_file_with_class_c, args=(ws, chunks, euis, process_code))
            print '开始新的线程...'
            new_thread.start()
            return jsonify({'progress_code': process_code})
        else:
            return '', 303


def _connet_socket(ws_url):
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
        _connet_socket(ws_url)


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


def slipe_file(file, step):
    """
    分割文件
    :param file: 要分割的文件
    :param step: 分割的大小
    :return:    分割成的碎片list
    """
    chunks = []
    while True:
        snippet = file.read(step)
        if not snippet:
            break
        chunks.append(snippet)

    return chunks


def send_file_with_timelimit(ws, chunks, euis, progress_code, timeout=3600):
    print '限时'
    timelimit(timeout, func=send_file_with_class_c, args=(ws, chunks, euis, progress_code))


def send_file(ws, chunks, euis, progress_code):
    """
    发送文件
    :param ws: websocket
    :param redis_conn: redis连接
    :param file: 待发送的文件
    :param euis: 发送的eui列表
    :param progress_code: 进度信息标志码
    :return:
    """
    start = datetime.now()
    redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password= REDIS_PASSWORD)

    if not ws:
        ws = _connet_socket(ws_url)
    done_count = 0
    packet_indexs = dict()

    if euis:
        all_packet_be_send = len(chunks) * len(euis)            # 进度衡量量，总需要的进度
        # 初始化index
        for x in xrange(len(euis)):
            packet_indexs[euis[x]] = -1

        print '正在接收消息。。。'
        pubsub = redis_conn.pubsub()
        pubsub.subscribe(euis)
        for item in pubsub.listen():

            now = datetime.now()
            if (now - start).seconds > TIME_OUT:
                print '超时'
                break

            if not isinstance(item['data'], basestring):
                continue
            recv_data = item['data']
            recv_data = json.loads(recv_data)

            if done_count >= len(euis):         # 如果全部已完成，停止
                print '发送完成'
                pubsub.close()
                break

            if recv_data.get('h'):
                continue
            eui = recv_data.get('EUI')
            if eui in euis and recv_data.get('data', None):
                data = recv_data['data']

                if data[:2] == 'a1' or data[:2] == 'A1':
                    index = get_index(data)

                    # 初始化, 复位
                    if packet_indexs[eui] == -1:
                        packet_indexs[eui] = 0
                        reset_data = wrap_data('00', eui, index=0, end=True)
                        ws.send(reset_data)
                        continue

                    # 若已经复位，确认index已归零，如若未归零，继续等待
                    if packet_indexs[eui] == 0 and index != 0:
                        reset_data = wrap_data('00', eui, index=0, end=True)
                        ws.send(reset_data)
                        continue

                    # 判断是否已经发送完最后一个包,是的话，不做处理
                    # index = packet_indexs[eui]
                    if index >= len(chunks):
                        done_count += 1
                        continue
                    # 发送数据，index为数据指定的index, 并重置各个eui的 packet index
                    send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks))))

                    print u'发送数据：' , send_data
                    print 'index:', index + 1
                    ws.send(send_data)
                    packet_indexs[eui] = index + 1
                    # 记录进度
                    current_progress = progress(packet_indexs, all_packet_be_send)
                    print '=' * 60
                    print '当前进度：', current_progress
                    print 'progress_code', progress_code
                    print '=' * 60
                    publish_progress(redis_conn, progress_code, current_progress)


def send_file_with_class_c(ws, chunks, euis, progress_code):
    """
    发送文件
    :param ws: websocket
    :param redis_conn: redis连接
    :param file: 待发送的文件
    :param euis: 发送的eui列表
    :param progress_code: 进度信息标志码
    :return:
    """

    start = datetime.now()

    redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password= REDIS_PASSWORD)
    if not redis_conn.ping():
            raise Exception('redis没连接')
    pubsub = redis_conn.pubsub()
    pubsub.subscribe(euis)

    if not ws:
        ws = _connet_socket(ws_url)
    done_count = 0
    packet_indexs = dict()

    if euis:
        all_packet_be_send = len(chunks) * len(euis)            # 进度衡量量，总需要的进度
        # 初始化index
        for x in xrange(len(euis)):
            packet_indexs[euis[x]] = -1

        print '发送通知'
        for e in euis:
            send_data = wrap_data('212342', e, index=1, end=True)
            ws.send(send_data)
            print '发送初始化完成', send_data

        print '正在接收消息。。。'

        for item in pubsub.listen():

            now = datetime.now()
            if (now - start).seconds > TIME_OUT:
                print '超时'
                break
            if not isinstance(item['data'], basestring):
                continue
            recv_data = item['data']
            recv_data = json.loads(recv_data)

            if done_count >= len(euis):         # 如果全部已完成，停止
                print '发送完成'
                pubsub.close()
                break

            if recv_data.get('h'):
                continue
            eui = recv_data.get('EUI')
            if eui in euis and recv_data.get('data', None):
                data = recv_data['data']

                if data[:2] == 'a1' or data[:2] == 'A1':
                    index = get_index(data)

                    # 判断是否已经发送完最后一个包,是的话，不做处理
                    # index = packet_indexs[eui]
                    if index >= len(chunks):
                        done_count += 1
                        continue
                    # 发送数据，index为数据指定的index, 并重置各个eui的 packet index
                    send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks))))

                    print u'发送数据：' , send_data
                    print 'index:', index + 1
                    print u'先睡2秒'
                    time.sleep(4)
                    # 记录进度
                    current_progress = progress(packet_indexs, all_packet_be_send)
                    print '=' * 60
                    print '当前进度：', current_progress
                    print 'progress_code', progress_code
                    print '=' * 60
                    publish_progress(redis_conn, progress_code, current_progress)
                    ws.send(send_data)
                    packet_indexs[eui] = index + 1



def get_index(data):
    """
    :param data:收到的信息
    :return: 信息中的序号
    """
    return int(data[2:4], 16)


def publish_progress(redis_conn, progress_code, progress, ex_time=3600):
    """
    :param redis_conn: redis connection
    :param progress_code: 进度标识码
    :param progress: 进度（0-100）， 100 表示完成
    :param ex_time: 存在时间，默认一个小时
    :return:
    """
    res = redis_conn.get(progress_code)
    redis_conn.set(progress_code, progress)
    if not res:
        redis_conn.expire(progress_code, ex_time)


def progress(packet_indexs, all):
    """
    :param packet_indexs: 现在已发送的各个eui对应的文件序号
    :param all: 所以的序号
    :return: 进度（0 - 100）
    """
    values = packet_indexs.values()
    sum = 0
    for v in values:
        sum += v
    return int((sum / all) * 100)

def on_open():
    pass


def init_eui(eui):
    pass

class SendFile(object):

    def __init__(self, ws_url, chunks=None, euis=None):
        # global ws_app
        # if not ws_app:
        self.ws_app = websocket.WebSocketApp(url=ws_url)
        self.chunks = chunks
        self.euis = euis

    def send(self):
        pass





if __name__ == '__main__':
    euis = ['BE7A000000000302']

    ws = websocket.WebSocket()
    f = open('/home/qitian/PycharmProjects/busad/server/test/1HelloWorld.TXT', 'rb')
    chunks = slipe_file(f, 15)

    redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password= REDIS_PASSWORD)
    if not redis_conn.ping():
        raise Exception('redis没连接')

    pubsub = redis_conn.pubsub()
    pubsub.subscribe(euis)

    # ws_app = websocket.WebSocketApp()
    # ws_app.on_open = ws_app()

    ws_url = 'wss://ap1.loriot.io/app?id=be7a009f&token=Rd6c66b0j2xi98cG6DW0Kg'
    ws.connect(ws_url)

    for eui in euis:
        send_data = {"data": "04000000000000000000000000000000", "cmd": "tx", "EUI": "BE7A000000000302", "port": "1"}
        # send_data = wrap_data('212342', 'BE7A000000000302', index=1, end=True)
        ws.send(json.dumps(send_data))
        print '发送初始化完成', send_data


    # while True:
    #     for item in pubsub.listen():
    #         print item['data']
    # while True:
    #     time.sleep(10)
        # index = 128
        # print bin(index |
    # 0x80)
        # print bin(index)
