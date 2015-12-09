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
from server.app.utils.ws_listenning import ws_app
from threading import Thread
from server.app.utils.tools import timeout

PACKET_SIZE = 15
TIME_OUT = 10
# r = strict_redis
redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
if not redis_conn.ping():
    raise Exception('redis没连接')


class Publish(Resource):

    # TODO:文件接收
    def post(self):
        f = request.files['file']

        euis = request.form.get('euis')
        if euis:

            euis = euis.split(',')
            chunks = slipe_file(f, PACKET_SIZE)
            process_code = uuid4().hex
            new_thread = threading.Thread(target=send_file_with_timelimit, args=(chunks, euis, process_code))
            # if LORIOT_PROTOCOL == 'class_c':
            #     new_thread = threading.Thread(target=send_file_with_timelimit, args=(chunks, euis, process_code))
            # else:
            #     new_thread = threading.Thread(target=send_file
            #                                   , args=(chunks, euis, process_code))

            print '开始新的线程...'
            try:
                new_thread.start()
            except Exception, e:
                print '*'* 120
                print e.message

            return jsonify({'progress_code': process_code})
        else:
            return '', 303


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


def send_file_with_timelimit(chunks, euis, progress_code):

    try:
        if LORIOT_PROTOCOL == 'class_c':
            send_file_with_class_c(chunks, euis, progress_code)
        else:
            send_file(chunks, euis, progress_code)
    except Exception, e:
        publish_progress(redis_conn, progress_code, 408)


@timeout(TIME_OUT)
def send_file(chunks, euis, progress_code):
    """
    发送文件
    :param ws: websocket
    :param redis_conn: redis连接
    :param file: 待发送的文件
    :param euis: 发送的eui列表
    :param progress_code: 进度信息标志码
    :return:
    """
    # redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password= REDIS_PASSWORD)

    ws = _connect_socket(ws_url)
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


@timeout(TIME_OUT)
def send_file_with_class_c(chunks, euis, progress_code):
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

    # redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
    # if not redis_conn.ping():
    #         raise Exception('redis没连接')
    pubsub = redis_conn.pubsub()
    pubsub.subscribe(euis)
    ws = _connect_socket(ws_url)
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


def init_euis(euis, ws):
    """
    初始化euis
    :param euis: eui列表
    :param ws: websocket 连接
    :return:
    """
    for eui in euis:
        send_data = wrap_data('212342', eui, index=1, end=True)
        ws.send(send_data)


@timeout(15)
def filter_euis(euis, ws, pubsub):
    """
    筛选不存在的eui
    :param euis: 要发送的eui列表
    :return: 有效的eui列表
    """
    init_euis(euis, ws)




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


if __name__ == '__main__':
    euis = ['BE7A000000000302']

    euis = ['1', '2', '3']

    @timeout(2)
    def del_ele(euis):
        del euis[2]
        time.sleep(3)
    try:
        del_ele(euis)
    except Exception, e:
        print euis


