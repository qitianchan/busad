# -*- coding: utf-8 -*-
from server.app.extensions import auth, bcrypt
from flask_restful import Resource
from flask import request, jsonify, g
from flask_restful import fields
import os
import websocket

import thread
import time
import json
import redis
import threading
from server.app.utils import strict_redis
from server.app.config import LORIOT_WEBSOCKET_URL as ws_url
from server.app.utils.ws_listenning import ws


GATEWAY_ID = "be7a0029"
TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"

# 目标设备信息
EUI = "BE7A00000000063A"
ADDR = "00aa1174"
LASTEST_SEQ = 0
APP_SKEY = "2b7e151628aed2a6abf7158809cf4f3c"

# 需要下载的文件
FILE_NAME = "3HelloNIOT.TXT"
PACKET_SIZE = 158

r = strict_redis

class Publish(Resource):

    # TODO:文件接收
    def post(self, ws):
        f = request.files['file']

        euis = request.form.get('euis')
        if euis:
            euis = euis.split(',')
            if ws == None:
                ws = _connet_socket(ws_url)

            new_thread = threading.Thread(target=send_file, args=(ws, f, euis))
            print '开始新的线程...'
            new_thread.start()


            return '上传成功', 201
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


def wrap_data(data, eui, index, end=False):
    # 包装将要发送的数据
    send_data = {"cmd": "tx", "EUI": "", "port": 1, "data": ""}
    send_data['EUI'] = eui
    data_head = int(str(index), 16) | 0x00
    if end:
        data_head = int(str(index), 16) | 0x80

    data_head = hex(data_head)[2:]
    send_data['data'] = data_head + data.encode('hex')
    return send_data


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


def send_file(ws, redis_conn, file, euis):
    """
    发送文件
    :param ws: websocket
    :param redis_conn: redis连接
    :param file: 待发送的文件
    :param euis: 发送的eui列表
    :return:
    """
    done_count = 0
    packet_indexs = dict()

    chunks = slipe_file(file, PACKET_SIZE)

    if euis:
        # euis = euis.split(',')
        # TODO
        # 初始化index
        for x in xrange(len(euis)):
            packet_indexs[euis[x]] = 0

        if ws == None:
            ws = _connet_socket(ws_url)

        print '正在接收消息。。。'
        pubsub = redis_conn.pubsub()
        pubsub.subscribe(euis)
        for item in pubsub.listen():

            if not isinstance(item['data'], basestring):
                continue
            recv_data = item['data']

        # while done_count < len(euis):          # 全部发送完成
            if done_count >= len(euis):         # 如果全部已完成，停止
                break

            if hasattr(recv_data, 'h'):
                continue
            eui = recv_data.get('EUI')
            if eui in euis and hasattr(recv_data, 'data'):
                data = recv_data['data']

                if data[:2] == 'a1' or data[:2] == 'A1':

                    # 判断是否已经发送完最后一个包,是的话，不做处理
                    index = packet_indexs[eui]
                    if index >= len(chunks):
                        done_count += 1
                        continue

                    # 包装好要发送的数据格式
                    send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks) - 1)))
                    print u'发送数据：' , send_data
                    print 'index:', index
                    ws.send(send_data)
                    packet_indexs[eui] += 1

                else:
                    # 重发数据，index为数据指定的index, 并重置各个eui的 packet index
                    index = int(recv_data[2:4], 16)
                    send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks) - 1)))

                    print u'发送数据：' , send_data
                    print 'index:', index
                    ws.send(send_data)
                    packet_indexs[eui] = index

            # TODO： 记录完成状态


def listen_redis(ws, connect_redis, euis):
    """

    :param ws:
    :param connect_redis:
    :param euis:
    :return:
    """
    pubsub = r.pubsub()
    pubsub.subscribe(euis)
    print 'Listing...'

    while True:
        if ws == None:
            ws = _connet_socket(ws_url)
        print '开始接收消息'
        recv_data = json.dumps(ws.recv())
        print recv_data

    count = 0
    for item in pubsub.listen():
        print item['data']
        count += 1
        if count > 5:
            print '发送结束'
            break

def recv_redis_message(redis_conn, euis):
    pubsub = redis_conn.pubsub()
    pubsub.subscribe(euis)
    while True:
        for item in pubsub.listen():
            print item['data']
            # todo: 处理接收到的信息

if __name__ == '__main__':
    pass

