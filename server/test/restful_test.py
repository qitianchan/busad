# -*- coding: utf-8 -*-
import requests
import json

with open('1HelloWorld.TXT', 'rb') as f:
    while True:
        chunk = f.read(15)
        chunk = chunk.encode('hex')
        if not chunk:
            break
