# -*- coding: utf-8 -*-
import signal
import time

def handler(sig, frame):
    print 'got signal', sig

signal.signal(signal.SIGABRT, handler)

now = time.time()
time.sleep(200)
print 'sleep for', time.time() - now, 'seconds'
