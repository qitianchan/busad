# -*- coding: utf-8 -*-

from sys import setcheckinterval

if __name__ == '__main__':
    from server.app.resources.sendfile.send_file import SendGroupMessage
    print('ahellsa')
    send = SendGroupMessage('dsfdasfsa', 'sdfasf', ['dfasf', 'dfasfas'], 'asdfaf','dsfdasfafs', package_length=2)
    print(send)