# -*- coding: utf-8 -*-
from flask import g
from socketIO_client import SocketIO, LoggingNamespace
from server.app.config import OURSELF_HOST, OURSELF_PORT, OURSELF_TOKEN, OURSELF_APP_EUI

import logging
logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)


with SocketIO(OURSELF_HOST, OURSELF_PORT, LoggingNamespace) as socketIO:
    socketIO.emit('aaa')
    socketIO.wait(seconds=1)


def get_current_user():
    pass