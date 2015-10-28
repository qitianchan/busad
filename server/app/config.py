import os
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')

DEBUG = True
WTF_CSRF_ENABLED = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
SECRET_KEY = 'This is a secret key, and it shuold be long long long and long enouth'

GATEWAY_ID = "be7a0029"
LORIOT_TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"
LORIOT_URL = "wss://www.loriot.io/app?id=" + GATEWAY_ID + "&token=" + LORIOT_TOKEN