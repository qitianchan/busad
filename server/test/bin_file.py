#-*- coding: utf-8 -*-

from flask import Flask
from request_test_api2 import get_db
from threading import Thread
from time import sleep

app = Flask(__name__)

if __name__ == '__main__':
    t1 = Thread(name='thread1',target=get_db, args=('hello',))
    print t1.name
    t1.start()
    print 't1:', t1
    t2 = Thread(name='thread2',target=get_db, args=('hello',), )
    print 't2:', t2
    t2.start()
    print '线程创建过了'
    sleep(1)
    a1 = get_db('hello')
    a2 = get_db('hello')
    a3 = get_db('ta2')