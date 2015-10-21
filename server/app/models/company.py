# -*- coding: utf-8 -*-
from flask import g
from wtforms.validators import Email

from server.app.main import db, bcrypt


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    # one-to-many
    users = db.relationship('User', backref=db.backref('company'))

