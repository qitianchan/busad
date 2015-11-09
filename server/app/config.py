import os
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')

DEBUG = True
WTF_CSRF_ENABLED = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
SECRET_KEY = 'This is a secret key, and it shuold be long long long and long enouth'

GATEWAY_ID = "be7a0029"
LORIOT_TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"
LORIOT_URL = "wss://www.loriot.io/app?id=" + GATEWAY_ID + "&token=" + LORIOT_TOKEN

LORIOT_BUFFER = "5b481368a8f69bc0df35b57e5a2775bb746be181274ef26947c3400fb9beb50326e4b3eb58627df9a75187a5d74d17c8b92e"
LORIOT_APP_SKEY = "2b7e151628aed2a6abf7158809cf4f3c"
LORIOT_ADDRESS = "6d609574"