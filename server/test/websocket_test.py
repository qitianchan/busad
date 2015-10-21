import websocket
import json
import time

GATEWAY_ID = "be7a0029"
TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"

send_data = {"cmd": "tx", "EUI": "BE7A0000000005D2", "port": 1, "data": "5659"}

ws = websocket.WebSocket()
ws.connect("wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN)
# while True:
#     ws.send(json.dumps(send_data))
#     time.sleep(5)

with open('restful-api.py', 'rb') as f:
    try:
        while True:
            chunk = f.read(10)
            hex_data = ''
            for i in xrange(len(chunk)):
                hex_data += hex(ord(chunk[i]))[2:]
            if not chunk:
                break
            print hex_data
            send_data['data'] = hex_data
            ws.send(json.dumps(send_data))

    finally:
        ws.close()


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


