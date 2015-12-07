import os
basedir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# max content length  10Kb
MAX_CONTENT_LENGTH = 10 * 1024

DEBUG = True
WTF_CSRF_ENABLED = False
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:aaaaa@localhost/busad?charset=utf8&use_unicode=0'
SECRET_KEY = 'This is a secret key, and it shuold be long long long and long enouth'
GATEWAY_ID = "be7a009f"
LORIOT_TOKEN = "Rd6c66b0j2xi98cG6DW0Kg"
LORIOT_URL = "wss://ap1.loriot.io/app?id=" + GATEWAY_ID + "&token=" + LORIOT_TOKEN
# GATEWAY_ID = "be7a0029"
# LORIOT_TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"
# LORIOT_URL = "wss://www.loriot.io/app?id=" + GATEWAY_ID + "&token=" + LORIOT_TOKEN
LORIOT_WEBSOCKET_URL = LORIOT_URL
LORIOT_PORT = '1'
LORIOT_PROTOCOL = 'class_c'             # class_a class_b class_c

LORIOT_BUFFER = "5b481368a8f69bc0df35b57e5a2775bb746be181274ef26947c3400fb9beb50326e4b3eb58627df9a75187a5d74d17c8b92e"
LORIOT_APP_SKEY = "2b7e151628aed2a6abf7158809cf4f3c"
LORIOT_ADDRESS = "6d609574"

# redis
REDIS_HOST = '183.230.40.230'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = 123456
REDIS_URL = 'redis://:123456@183.230.40.230:6379'
