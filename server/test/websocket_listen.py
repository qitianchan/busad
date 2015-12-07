import websocket
import json
import time
from server.app.config import LORIOT_URL as url

euis = ['BE7A0000000005D2', 'BE7A0000000005C1']

send_data = {"cmd": "tx", "EUI": "BE7A0000000005D2", "port": 1, "data": "5659"}


def on_message(ws, message):
    print message

if __name__ == '__main__':
    # while True:
    #     data = ws.recv()
    #     print data
    ws_app = websocket.WebSocketApp(url=url,
                                    on_message=on_message)
    ws_app.run_forever()

