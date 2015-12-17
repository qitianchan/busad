from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with
from flask_restful import Resource
import flask_restful as restful
from server.app.extensions import db, bcrypt, auth
from server.app.models import User
from  sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
import json
import time

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'role': fields.Integer,
    'phone': fields.String,
    'company_name': fields.String,
    'progress_code': fields.String
}


class UserInfo(Resource):
    decorators = [auth.login_required]

    @marshal_with(user_fields)
    def get(self, nothing_to_do):
        return g.user, 201