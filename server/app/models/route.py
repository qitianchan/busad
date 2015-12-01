# -*- coding: utf-8 -*-
from flask import g
from wtforms.validators import Email
from server.app.extensions import db, bcrypt
from server.app.models.bus import Bus
from sqlalchemy.exc import IntegrityError


class Route(db.Model):
    __tablename__ = 'route'
    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    route_name = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=1)                   # 可用标志位， 0 不可用， 1 可用（删除）

    # one-to-many
    buses = db.relationship('Bus', backref=db.backref('route'))

    def __init__(self, district_id, route_name):
        self.district_id = district_id
        self.route_name = route_name
        self.user_id = g.user.id

    def __repr__(self):
        return '<Route %s>' % self.route_name

    @classmethod
    def get_routes(cls):
        return cls.query.filter(Route.user_id == g.user.id).all()

    @classmethod
    def get(cls, route_id):
        return cls.query.filter(Route.id == route_id).first()

    @classmethod
    def delete(cls, route_id):
        bus = Bus.query.filter(Bus.route_id == route_id).first()
        if bus:
            raise IntegrityError(u'数据完整性异常')
        del_obj = cls.get(route_id)
        db.sessoin.delete(del_obj)
        db.session.commit()
