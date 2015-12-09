# -×- coding:utf-8 -*-
from flask import g
from flask_restful import Resource
from threading import Thread
import threading
import time
from datetime import datetime


class TimeoutThread(Thread):
    def __init__(self):
        super(TimeoutThread, self).__init__()

    def run(self):
        tt = TestThread()
        tt.start()
        time.sleep(50)
        tt.stop()


class TestThread(Thread):
    def __init__(self):
        super(TestThread, self).__init__()
        self._stop = False
        self.count = 0

    def run(self):
        while not self._stop and self.count < 3:
            print datetime.now()
            time.sleep(2)
            self.count += 1
        print u'结束'

    def stop(self):
        self._stop = True


class AbortTest(Resource):
    def get(self):

        tt = TimeoutThread()
        tt.start()

        print u'返回'
        return ''

    def put(self):
        g.keeping = False
        return ''

