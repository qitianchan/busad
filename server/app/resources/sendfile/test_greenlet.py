# # -*- coding: utf-8 -*-
from greenlet import greenlet, getcurrent
import time
def test1():
    print 12
    gr2.parent.switch()
    print 34

def test2():
    print 56
    gr1.switch()
    print 78
gr1 = greenlet(test1)
gr2 = greenlet(test2)

def get_ack():
    while True:
        time.sleep(2)
        gl_self = getcurrent()
        gl_self.parent.switch()

gl_ack = greenlet(get_ack)
for i in range(7):
    print('send message %s' %i)
    gl_ack.switch()