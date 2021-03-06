# -*- coding: utf-8 -*-
import os
from flask import Flask, g
import flask_restful as restful
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.httpauth import HTTPBasicAuth
from extensions import db, bcrypt, auth
from resources import api
from server.app.models import User
from threading import Thread
import redis
import websocket
from utils.ws_listenning import wrap_listen, ws_listening, Listening
from server.app.config import LORIOT_URL
from server.app.resources.command import command
# GATEWAY_ID = "be7a0029"
# TOKEN = "7AXCO2-Kkle42YGVVKvmmQ"
#
# url = "wss://www.loriot.io/app?id="+GATEWAY_ID+"&token="+TOKEN

# 创建app，并且配置扩展
def create_app():

    app = Flask(__name__)
    app.config.from_object('server.app.config')
    init_app(app)
    config_extensions(app)
    with app.app_context():
        db.create_all()

    return app


# 配置扩展
def config_extensions(app):
    db.init_app(app)
    api.init_app(app)
    bcrypt.init_app(app)

    # 配置验证, HTTP BASE Authenticate
    @auth.verify_password
    def verify_password(username_or_token, password):
        # first tyr to authenticate by token
        user = User.virify_auth_token(username_or_token)
        if not user:
            # try to authenticate by token

            user = User.query.filter_by(username=username_or_token).first()
            # user = User.get_user_by_name(username_or_token)
            if not user or not user.verify_password(password):
                return False
        g.user = user
        return True


# app = create_app()

def init_app(app):
    app.register_blueprint(command, url_prefix='/api/command')
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    # @app.before_first_request
    # def before_first_request():
    #     try:
    #         # listen = Listening()
    #         ws = websocket.WebSocket()
    #         ws.connect(LORIOT_URL)
    #
    #         ws_listening_thread = Thread(target=ws_listening)
    #         ws_listening_thread.start()
    #     except Exception, e:
    #         print e.message
    #         raise e

if __name__ == '__main__':
    app = create_app()
    app.run()
