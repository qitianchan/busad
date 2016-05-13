# -*- coding: utf-8 -*-
from flask import g
from wtforms.validators import Email

from server.app.extensions import db, bcrypt


class Bus(db.Model):
    __tablename__ = 'bus'
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    group_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plate_number = db.Column(db.String(16), unique=True)                # 车牌号
    light_number = db.Column(db.String(16))                             # 车灯号
    eui = db.Column(db.String(64), unique=True)                         # 广告发送模块ID

    def __init__(self, route_id, plate_number, light_number=None, eui=None):
        self.route_id = route_id
        self.plate_number = plate_number
        self.user_id = g.user.id
        if light_number:
            self.light_number = light_number
        if eui:
            self.eui = eui

    def __repr__(self):
        return '<Bus %s>' % self.plate_number

    @classmethod
    def get_bus_list(cls):
        return cls.query.filter(Bus.user_id == g.user.id).all()

    @classmethod
    def get(cls, bus_id):
        return cls.query.filter(Bus.id == bus_id).first()

    @classmethod
    def get_buses_by_route(cls, route_id):
        return cls.query.filter(Bus.route_id == route_id).all()

    def update_bus(self,route_id=None, plate_number=None, light_number=None, eui=None):
        if route_id:
            self.route_id = route_id
        if plate_number:
            self.plate_number = plate_number
        if light_number:
            self.light_number = light_number
        if eui:
            self.eui = eui

