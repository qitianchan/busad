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

PACKET_SIZE = 15

r = strict_redis

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

            new_thread = threading.Thread(target=send_file, args=(ws, r, chunks, euis))
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


def send_file(ws, redis_conn, chunks, euis):
    """
    发送文件
    :param ws: websocket
    :param redis_conn: redis连接
    :param file: 待发送的文件
    :param euis: 发送的eui列表
    :return:
    """

    if not ws:
        ws = _connet_socket(ws_url)
    done_count = 0
    packet_indexs = dict()

    if euis:
        # euis = euis.split(',')
        # TODO
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
                            continue

                    # 判断是否已经发送完最后一个包,是的话，不做处理
                    # index = packet_indexs[eui]
                    if index >= len(chunks):
                        done_count += 1
                        continue
                #
                #     # 包装好要发送的数据格式
                #     send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks) - 1)))
                #     print u'发送数据：' , send_data
                #     # send_data = '{"data": "04c43584247313656312e3000000000000", "cmd": "tx", "EUI": "BE7A000000000301", "port": "1"}'
                #     print 'index:', index
                #     ws.send(send_data)
                #     packet_indexs[eui] += 1
                #
                # elif data[:2] == 'a2' or data[:2] == 'A2':
                    # 重发数据，index为数据指定的index, 并重置各个eui的 packet index
                    send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks))))

                    print u'发送数据：' , send_data
                    print 'index:', index + 1
                    ws.send(send_data)
                    packet_indexs[eui] = index + 1

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

def get_index(data):
    return int(data[2:4], 16)

if __name__ == '__main__':
    ws = websocket.WebSocket()
    ws_url = 'wss://ap1.loriot.io/app?id=be7a009f&token=Rd6c66b0j2xi98cG6DW0Kg'
    ws.connect(ws_url)
    send_data = {'cmd': 'tx', 'EUI': 'BE7A000000000301', 'port': '1', 'data': '043412'}
    send_data = {"data": "8600000000000000000000000000000060000000000000000000007a00010302", "cmd": "tx", "EUI": "BE7A000000000301", "port": LORIOT_PORT}
    while True:
        ws.send(json.dumps(send_data))
        print '发送完成', json.dumps(send_data)
        time.sleep(10)
    # index = 128
    # print bin(index | 0x80)
    # print bin(index)

