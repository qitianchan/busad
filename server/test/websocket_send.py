import websocket
import json
import time
from binascii import unhexlify
# from server.app.libs.loraencrypto.loraCrypto import LoRaCrypto

Buffer = unhexlify("5b481368a8f69bc0df35b57e5a2775bb746be181274ef26947c3400fb9beb50326e4b3eb58627df9a75187a5d74d17c8b92e")
AppSKey = unhexlify("2b7e151628aed2a6abf7158809cf4f3c")
address = '00AA1174'
direction = 0
sequenceCounter = 1



GATEWAY_ID = "be7a0029"
TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"

url = "wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN

send_data = {"cmd": "tx", "EUI": "BE7A00000000063A", "port": 1, "data": "5659"}

ws = websocket.WebSocket()


ws.connect("wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN)
# while True:
#     ws.send(json.dumps(send_data))
#     time.sleep(5)

DATA = [
    '0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0b00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff',
    '0f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff'
]

with open('request_test_api.py', 'rb') as f:
    try:
        # while True:
        #     chunk = f.read(48)
        #     send_data['data'] = chunk.encode('hex')
        #     res = ws.send(json.dumps(send_data))
        #     print hex_data
        #     print 'return:', res
        #     time.sleep(2)
        while True:
            for i in xrange(len(DATA)):
                data = DATA[i]
                # send_data['data'] = LoRaCrypto().payload_encrypt(data, AppSKey, address, direction, sequenceCounter)
                send_data['data'] = data
                res = ws.send(json.dumps(send_data))
                print data
                print res
                time.sleep(10)

    finally:
        ws.close()


def send_file(f, ws, eui):
    pass

# def send_file(file, )
# try:
#     while True:
#         ws.send(json.dumps(send_data))
#         recv_data = json.loads(ws.recv())
#         if recv_data != None:
#             print(recv_data)
#         time.sleep(10)
# except KeyboardInterrupt:
#     print("exit")
#     ws.close()


def on_message(ws, message):
    print message

# if __name__ == '__main__':
#     ws_app = websocket.WebSocketApp(url=url,
#                                     on_message=on_message)
#
#     ws_app.run_forever()

