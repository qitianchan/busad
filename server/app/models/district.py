# -*- coding: utf-8 -*-
from flask import g
from wtforms.validators import Email

from server.app.extensions import db, bcrypt


class District(db.Model):
    __tablename__ = 'district'
    id = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # one-to-many
    routes = db.relationship('Route', backref=db.backref('district'))

    def __init__(self, district_name):
        self.district_name = district_name
        self.user_id = g.user.id

    def __repr__(self):
        return '<District %r>' % self.district_name

    # district list
    @classmethod
    def get_district_list(cls):
        if hasattr(g, 'user'):
            return cls.query.filter(District.user_id == g.user.id).all()

    @classmethod
    def get(cls, district_id):
        if hasattr(g, 'user'):
            return cls.query.filter(District.id == district_id).first()

    def update_distrct(self, district_name):
        self.district_name = district_name
