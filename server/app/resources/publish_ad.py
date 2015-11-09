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



def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print "thread terminating..."
    thread.start_new_thread(run, ())

#
# if __name__ == "__main__":
#     websocket.enableTrace(True)
#     ws = websocket.WebSocketApp("ws://echo.websocket.org/",
#                               on_message = on_message,
#                               on_error = on_error,
#                               on_close = on_close)
#     ws.on_open = on_open
#     ws.run_forever()

ws = websocket.WebSocket()

class Publish(Resource):

    # TODO:文件接收
    def post(self):
        f = request.files['file']
        done_count = 0                                  # 发送完成的数量
        chunks = slipe_file(f,PACKET_SIZE)              # 读取的包


        packet_indexs = dict()                          # 对应的eui当前的包序号

        euis = request.form.get('euis')
        if euis:
            euis = euis.split(',')
            # TODO
            # 初始化index
            for x in xrange(len(euis)):
                packet_indexs[euis[x]] = 0


            print '正在连接。。。'
            try:
                _connet_socket(ws, "wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN)
            except:
                _connet_socket(ws, "wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN)

            print '正在接收消息。。。'
            while done_count != len(euis):          #全部发送完成
                recv_data = json.loads(ws.recv())
                if recv_data.has_key('h'):
                    continue
                eui = recv_data.get('EUI')
                if eui in euis and recv_data.has_key('data'):
                    data = recv_data['data']
                    if data[:2] == 'a1' or data[:2] == 'A1':
                        # send in a normal sequence
                        # todo

                        # 判断是否已经发送完最后一个包,是的话，不做处理
                        index = packet_indexs[eui]
                        if index >= len(chunks):
                            done_count += 1
                            continue

                        # 包装好要发送的数据格式
                        send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks) - 1)))

                        ws.send(send_data)
                        packet_indexs[eui] += 1

                    else:
                        index = int(recv_data[2:4], 16)
                        send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks) - 1)))
                        ws.send(send_data)
                        packet_indexs[eui] = index

            return '上传成功', 201
        else:
            return '', 201

    def _send_file(self, euis, file):
        #   TODO: 发送文件到
        while(True):
            chunk = file.read(50)
            if not chunk:
                break

            # todo: 传输到设备
            for eui in euis:
                print eui, ':', chunk.encode('hex')


def _connet_socket(ws, url="wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN):
    try:
        ws.connect(url)
    except Exception:
        ws.connect(url)




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


def send_file(ws, file, euis):
    done_count = 0
    packet_indexs = dict()

    chunks = slipe_file(file, PACKET_SIZE)

    if euis:
        euis = euis.split(',')
        # TODO
        # 初始化index
        for x in xrange(len(euis)):
            packet_indexs[euis[x]] = 0


        print '正在连接。。。'
        ws.connect("wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN)

        print '正在接收消息。。。'
        while done_count == len(euis):          #全部发送完成
            recv_data = json.loads(ws.recv())
            if hasattr(recv_data, 'h'):
                continue
            eui = recv_data.get('EUI')
            if eui in euis and hasattr(recv_data, 'data'):
                data = recv_data['data']
                if data[:2] == 'a1' or data[:2] == 'A1':
                    # send in a normal sequence
                    # todo

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
                    index = int(recv_data[2:4], 16)
                    send_data = wrap_data(chunks[index], eui, index, end=(index == (len(chunks) - 1)))

                    print u'发送数据：' , send_data
                    print 'index:', index
                    ws.send(send_data)
                    packet_indexs[eui] = index


def hello():
       print 'hello'
       yield
       print 'world'
       yield
if __name__ == '__main__':
    import time
    h = hello()
    h.next()
    print 'Outside'
    time.sleep(3)
    h.next()

