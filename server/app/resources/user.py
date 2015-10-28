# -*- coding: utf-8 -*-
from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with

import flask_restful as restful
from server.app.extensions import db, bcrypt, auth
from server.app.models import User
from  sqlalchemy import and_


user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'company': fields.String
}

post_parser = reqparse.RequestParser()

post_parser.add_argument(
    'username', dest='username',
    type=str, location='form',
    required=True, help='The user\'s username'
)


class UserAPI(restful.Resource):
    decorators = [auth.login_required]

    @marshal_with(user_fields)
    def get(self, id):
        users = User.get(id)
        return users

    def put(self, id):
        pass

    def delete(self, id):
        pass


class UserList(restful.Resource):
    decorators = [auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, location='form', required=True,
                                   help='No username provided')
        self.reqparse.add_argument('password', type=str, location='form', required=True,
                                   help='No password provided')

    # 获取用户列表
    @marshal_with(user_fields)
    def get(self):
        users = User.get_user_list()
        return users

    # 创建新用户
    @marshal_with(user_fields)
    def post(self):
        if request.form:
            username = request.json.get('username')
            password = request.json.get('password')
            phone = request.json.get('phone')
            email = request.json.get('email')
            company = request.json.get('company')

            if username is None or password is None:
                abort(400)                              # missing arguments

            if User.query.filter_by(username=username).first() is not None:
                abort(400)                                              # existing user
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return user, 201

        else:
            abort(400)


class AuthToken(restful.Resource):
    @auth.login_required
    def get(self):
        token = g.user.generate_auth_token()
        return jsonify({'token': token.decode('ascii')})
