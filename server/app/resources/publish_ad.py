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
from server.app.config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, LORIOT_PROTOCOL
from threading import Thread
from server.app.utils.tools import timeout
import copy

temp_euis = []
PACKET_SIZE = 48
TIME_OUT = 3600
# r = strict_redis
redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
if not redis_conn.ping():
    raise Exception('redis没连接')

# TODO: redis 修改为 hash
# progress:
#   progress_code
#   progress_code.error
#   progress_code.stop


class Publish(Resource):

    # TODO:文件接收
    def post(self):
        f = request.files['file']

        euis = request.form.get('euis')
        user_id = request.form.get('user_id')
        if euis:

            euis = euis.split(',')
            chunks = slipe_file(f, PACKET_SIZE)
            # 获取最后一次的progress_code, 并且终止掉（设置stop值为1）
            progress_code = uuid4().hex
            current_user = User.get(user_id)
            if not current_user:
                return '参数错误', 422

            last_progress_code = current_user.progress_code
            if last_progress_code:
                set_stop_progress(redis_conn, last_progress_code)
            # 更换progress_code
            current_user.progress_code = progress_code
            current_user.save()
            new_thread = threading.Thread(target=send_file_with_timelimit, args=(chunks, euis, progress_code, last_progress_code))

            print '开始新的线程...'
            try:
                new_thread.start()
            except Exception, e:
                print '*' * 120
                print e.message

            return jsonify({'progress_code': progress_code})
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


def send_file_with_timelimit(chunks, euis, progress_code, last_progress_code):

    try:
        if LORIOT_PROTOCOL == 'class_c':
            send_file_with_class_c(chunks, euis, progress_code, last_progress_code)
        else:
            send_file(chunks, euis, progress_code, last_progress_code)
    except Exception, e:
        publish_progress(redis_conn, progress_code, 408)


@timeout(TIME_OUT)
def send_file(chunks, euis, progress_code, last_progress_code):
    """
    发送文件
    :param ws: websocket
    :param redis_conn: redis连接
    :param file: 待发送的文件
    :param euis: 发送的eui列表
    :param progress_code: 当前进度信息标志码
    :param last_progress_code: 最后一次进度信息标志码
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
def send_file_with_class_c(chunks, euis, progress_code, last_progress_code):
    """
    发送文件
    :param ws: websocket
    :param redis_conn: redis连接
    :param file: 待发送的文件
    :param euis: 发送的eui列表
    :param progress_code: 当前进度信息标志码
    :param last_progress_code: 最后一次的进度信息标志码
    :return:
    """
    print '进入发送阶段...'
    pubsub = redis_conn.pubsub()
    pubsub.subscribe(euis)
    print '连接websocket。。。'
    ws = _connect_socket(ws_url)
    print '连接成功'
    done_count = 0
    packet_indexs = dict()

    # euis存在或者没有被停止
    if euis and not is_stopped(redis_conn, progress_code):

        all_packet_be_send = len(chunks) * len(euis)            # 进度衡量量，总需要的进度
        # 初始化index
        for x in xrange(len(euis)):
            packet_indexs[euis[x]] = -1

        try:

            filter_euis(euis, ws, pubsub)
            time.sleep(2)
        except Exception, e:
            publish_progress(redis_conn, progress_code, 408)
            error = progress_code + '.error'
            error_message = 'EUI: '
            for e in euis:
                if e not in temp_euis:
                    error_message += (e + ', ')
            error_message += 'out off power or not exits'
            publish_progress(redis_conn, error, error_message)

            print '过滤超时'
            raise

        euis = temp_euis
        # send first package
        index = 0
        for eui in euis:
            # time.sleep(4)
            send_data = wrap_data(chunks[index], eui, index, end=(index+1 == (len(chunks))))
            print '开始......'
            print '发送数据：', send_data
            ws.send(send_data)
            packet_indexs[eui] = index

        print '正在接收消息 。。。'

        for item in pubsub.listen():
            if is_stopped(redis_conn, progress_code):
                print '中止'
                break

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

                    # 判断是否已经发送完最后一个包,是的话，不做处理
                    # index = packet_indexs[eui]
                    if index >= len(chunks):
                        done_count += 1
                        if done_count >= len(euis):         # 如果全部已完成，停止
                            print '发送完成'
                            pubsub.close()
                            break
                        continue
                    # 发送数据，index为数据指定的index, 并重置各个eui的 packet index
                    # send_data = wrap_data(chunks[index], eui, index, end=(index+1 == len(chunks)))
                    send_data = wrap_data(chunks[index], eui, index, end=False)

                    print 'index:', index + 1
                    # print u'先睡2秒'
                    # time.sleep(4)
                    # 记录进度
                    packet_indexs[eui] = index + 1
                    current_progress = progress(packet_indexs, all_packet_be_send)
                    print '=' * 60
                    print '当前进度：', current_progress
                    print 'progress_code', progress_code
                    print '=' * 60
                    publish_progress(redis_conn, progress_code, current_progress)
                    ws.send(send_data)
                    print u'发送数据：' , send_data


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


@timeout(30)
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
    # res = redis_conn.get(progress_code)
    # redis_conn.set(progress_code, progress)
    # if not res:
    #     redis_conn.expire(progress_code, ex_time)
    _set_redis_with_expire(redis_conn, progress_code, progress, ex_time)


def set_stop_progress(redis_conn, progress_code, ex_time=3600):
    """

    :param redis_conn: redis connection
    :param progress_code_stop: progress_code + '.stop'
    :param ex_time: 存在时间，默认一个小时
    :return:
    """
    progress_code_stop = progress_code + '.stop'

    _set_redis_with_expire(redis_conn, progress_code_stop, 1, ex_time)


def is_stopped(r, progress_code):
    """
    是否应该停止
    :param r: redis connection
    :param progress_code:
    :return:
    """
    name = progress_code + '.stop'
    stop = r.get(name)
    if stop > 0:
        return True
    return False


def _set_redis_with_expire(redis_conn, name, value, ex_time):
    """
    设置存在时间为 ex_time的一个 redis值
    :param redis_conn: redis connection
    :param name:
    :param value:
    :param ex_time:
    :return:
    """
    res = redis_conn.get(name)
    redis_conn.set(name, value)
    if not res:
        redis_conn.expire(name, ex_time)


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

    euis = ['1', '2', '3', [1,2,3]]

    copy_euis = copy.copy(euis)
    euis = []

    del copy_euis[2]
    print copy_euis
    deep_euis = copy.deepcopy(euis)
    print deep_euis
