import websocket
import json
import time

GATEWAY_ID = "be7a0029"
TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"

url = "wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN
euis = ['BE7A0000000005D2', 'BE7A0000000005C1']

send_data = {"cmd": "tx", "EUI": "BE7A0000000005D2", "port": 1, "data": "5659"}

ws = websocket.WebSocket()


ws.connect("wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN)


def on_message(ws, message):
    print message

if __name__ == '__main__':
    # while True:
    #     data = ws.recv()
    #     print data
    ws_app = websocket.WebSocketApp(url=url,
                                    on_message=on_message)
    ws_app.run_forever()

