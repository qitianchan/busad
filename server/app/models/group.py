# -*- coding: utf-8 -*-
from flask import g
from wtforms.validators import Email
from server.app.extensions import db, bcrypt
from server.app.models.bus import Bus
from sqlalchemy.exc import IntegrityError


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    eui = db.Column(db.String(32), unique=True)
    group_id = db.Column(db.String(8), unique=True)


    @property
    def buses(self):
        return Bus.query.filter(Bus.group_id == self.id).all()

    def __init__(self, group_name, group_id, group_eui=None):
        self.group_name = group_name
        self.user_id = g.user.id
        self.group_id = group_id
        self.eui = group_eui

    def __repr__(self):
        return '<Group %s>' % self.group_name

    @classmethod
    def get_groups(cls):
        return cls.query.filter(Group.user_id == g.user.id).all()

    @classmethod
    def get(cls, group_id):
        return cls.query.filter(Group.id == group_id).first()

    @classmethod
    def delete(cls, group_id):
        buses = Bus.query.filter(Bus.group_id == group_id).all()
        del_obj = cls.get(group_id)
        db.session.delete(del_obj)

        if buses:
           for bus in buses:
                bus.group_id = None
                db.session.add(bus)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        pass

    def remove(self):
        buses = Bus.query.filter(Bus.group_id == self.id).all()
        db.session.delete(self)

        if buses:
           for bus in buses:
                bus.group_id = None
                db.session.add(bus)
        db.session.commit()