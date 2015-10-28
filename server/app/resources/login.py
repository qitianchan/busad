# -*- coding: utf-8 -*-
from server.app.extensions import auth, bcrypt
from flask_restful import Resource
from flask import request, jsonify
from server.app.models import User
from flask_restful import fields
user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'company': fields.String,
    'role': fields.Integer

}


class Login(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        user = User.get_user_by_name(username)
        if user and user.verify_password(password):
            token = user.generate_auth_token()
            print token
            return jsonify({'token': token})
        return '', 401
