# -*- coding:utf-8 -*-
import websocket
import json
import time
from loraCrypto2 import LoRaCrypto
from binascii import hexlify
from pickle import dump, load
import os

'''
没有加密的数据
{
	cmd: 'tx';
	EUI: string;
	port: number;
	data: string
}

加密的数据
{
	cmd: 'tx';
	EUI: string;
	port: number;
	encdata: string;
	seqno: number;
}
'''

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


sendData = {}

def main():
    ws = websocket.WebSocket()
    ws.connect("wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN)
    lc = LoRaCrypto()

    with open(FILE_NAME, "rb") as downloadFile:
        binData =downloadFile.read()

    count = len(binData) # PACKET_SIZE

    sendData["cmd"] = "tx"
    sendData["EUI"] = EUI
    sendData["port"] = 1
   
    # if "seq.p" in os.listdir()
    seq = LASTEST_SEQ

    print("Upload start!")
    for i in range(count+1):
        packetBin = binData[i*PACKET_SIZE:i*PACKET_SIZE+PACKET_SIZE]
        packetStr = hexlify(packetBin).decode()
        packetEncStr = lc.PayloadEncrypt(packetStr, APP_SKEY, ADDR, 1, seq)
        sendData["encdata"] = packetEncStr
        sendData["seqno"] = seq

        print("Packet %d:" % i)
        print("Before encrypt:")
        print(packetStr)
        print("After encrypt:")
        print(packetEncStr)
        print("Sequence is %d" % seq)
        res = ws.send(json.dumps(sendData))
        seq += 1
        
        time.sleep(10)
    
    print("Upload finish!")
    ws.close()

def send_file(ad_file, euis, step=48):
    chunk = ad_file.read(step)


class BillBoardSocket(object):

    def __init__(self, url, gayway_id, token ):
        if not isinstance(url, basestring) or not isinstance(gayway_id, basestring) or not isinstance(token, basestring):
            raise ValueError(u'url 和 gayway_id 和 token 必须为字符串')
        websocket_url = url + '?id=' + gayway_id + "&token="+TOKEN
        self.ws = websocket.WebSocket()
        self.ws.connect(websocket_url)

    def send_file(self, file, euis, step=48):
        lc = LoRaCrypto()
        send_data = {}
        while(True):
            chunk = file.read(step)
            if not chunk:
                break

        send_data["cmd"] = "tx"
        send_data["port"] = 1

        if isinstance(euis, list):
            for i in xrange(len(euis)):
                send_data['EUI'] = euis[i]









if __name__ == "__main__":
    main()





