# -*- coding: utf-8 -*-
from threading import Thread
class TimeLimitExpired(Exception): pass
import time
from server.test import hello

def timelimit(timeout, func, args=(), kwargs={}):
    """ Run func with the given timeout. If func didn't finish running
        within the timeout, raise TimeLimitExpired
    """
    import threading
    class FuncThread(Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            self.result = func(*args, **kwargs)

        def _stop(self):
            if self.isAlive():
                Thread._Thread__stop(self)

    it = FuncThread()
    it.start()
    it.join(timeout)
    if it.isAlive():
        it._stop()
        raise TimeLimitExpired()
    else:
        return it.result


def test(timeout):
    i = 0
    while True:
        i += 1
        print i
        time.sleep(1)

timelimit(10, func=test, args=(30,))
