# -*- coding: utf-8 -*-
from threading import Thread
from time import sleep

class Timeout(Thread):
    def __init__(self):
        super(Timeout, self).__init__()
        self.exitcode = 0
        self.exception = None
        self.ext_traceback = ''

    def run(self):
        try:
            sleep(2)
            print 'sleeppppy'
            raise Exception
        except Exception, e:
            self.exitcode = -1


if __name__ == '__main__':
    t1 = Timeout()
    t1.start()
    t1.join()
    if t1.exitcode != 0:
        raise Exception
    sleep(100)
    print '主线程'