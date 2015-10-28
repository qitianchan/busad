# -*- coding: utf-8 -*-
from websocket import WebSocketApp
from server.app.config import LORIOT_URL
from flask import g

def detect_missing_data(ws, message):
    # todo: 探测丢失信号
    print message
    if hasattr(g, 'user'):
        print g.user

ws_app = WebSocketApp(url=LORIOT_URL, on_message=detect_missing_data)