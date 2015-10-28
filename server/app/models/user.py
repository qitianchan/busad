# -*- coding: utf-8 -*-
from flask import g
from wtforms.validators import Email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from server.app.extensions import db, bcrypt
from sqlalchemy import and_
# from server.app.main import app
from server.app.config import SECRET_KEY


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, info={'validators': Email()})
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.SmallInteger, default=1)                               # 超级管理员：0， 管理员：1， 一般员工：2
    status = db.Column(db.SmallInteger, default=1)                             # 0 不可以， 1 可用
    phone = db.Column(db.String(128))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company_name = db.Column(db.String(128))
    token = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.email

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def generate_auth_token(self, expiration=24*60*60):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def virify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None     # valid token, but expired
        except BadSignature:
            return None     # invalid token
        user = User.query.get(data['id'])
        return user

    @classmethod
    def get_user_list(self):
        return self.query.filter(and_(User.status == 1, User.role == 1)).all()

    @classmethod
    def get(cls, user_id):
        return cls.query.filter(User.id == user_id).first()

    @classmethod
    def get_user_by_name(cls, username):
        return cls.query.filter(User.username == username).first()

