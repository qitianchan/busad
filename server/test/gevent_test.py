# from gevent.monkey import patch_all; patch_all()
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify
from time import sleep
import time
import websocket
app = Flask(__name__)
app.debug = True
from threading import Thread


@app.route('/long-polling')
def long_polling():
    url = 'wss://ap1.loriot.io/app?id=be7a009f&token=Rd6c66b0j2xi98cG6DW0Kg'

    start = time.time()
    send_data = {"cmd": "tx", "EUI": "BE7A00000000063A", "port": 1, "data": "5659"}

    ws = websocket.WebSocket()
    ws.connect(url)
    ws.connect(url)
    ws.connect(url)
    end = time.time()
    duration = end - start
    return 'connect to websocket success, %s' % duration


@app.route('/')
def index():
    return 'index'

thread_ids = []


class TestThread(Thread):
    def run(self):
        global thread_ids
        thread_ids.append(self)


if __name__ == '__main__':
    # server = WSGIServer(('127.0.0.1', 6543), app)
    # server.serve_forever()
    # app.run(port=6543)
    t1 = TestThread()
    t2 = TestThread()
    t1.start()
    t2.start()

