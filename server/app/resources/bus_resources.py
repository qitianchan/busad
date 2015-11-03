# -*- coding: utf-8 -*-
from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with
from flask_restful import Resource
import flask_restful as restful
from server.app.extensions import db, bcrypt, auth
from server.app.models import Bus
from  sqlalchemy import and_


bus_fields = {
    'id': fields.Integer,
    'route_id': fields.Integer,
    'plate_number': fields.String,
    'light_number': fields.String,
    'eui': fields.String
}


class BusList(Resource):
    decorators = [auth.login_required]

    @marshal_with(bus_fields)
    def get(self):
        buses = Bus.get_bus_list()
        return buses, 201

    @marshal_with(bus_fields)
    def post(self):
        route_id = request.json.get('route_id')
        plate_number = request.json.get('plate_number')
        light_number = request.json.get('light_number')
        eui = request.json.get('eui')
        if not plate_number or not light_number:
            return jsonify({'code':'30', 'msg': 'plate_number and light_number should be exit'})
        bus = Bus(route_id, plate_number, light_number=light_number, eui=eui)

        try:
            db.session.add(bus)
            db.session.commit()
            return bus, 201
        except Exception, e:
            db.session.rollback()
            raise e


class BusAPI(Resource):
    decorators = [auth.login_required]

    @marshal_with(bus_fields)
    def get(self, id):
        bus = Bus.get(id)
        return bus, 201

    @marshal_with(bus_fields)
    def put(self, id):
        bus = Bus.get(id)
        route_id = request.json.get('route_id')
        plate_number = request.json.get('plate_number')
        light_number = request.json.get('light_number')
        eui = request.json.get('eui')

        bus.update_bus(route_id=route_id, plate_number=plate_number, light_number=light_number, eui=eui)
        db.session.add(bus)
        db.session.commit()
        return bus, 201

    @marshal_with(bus_fields)
    def delete(self, id):
        bus = Bus.get(id)
        try:
            db.session.delete(bus)
            db.session.commit()
            return Bus.get_bus_list()

        except Exception, e:
            db.session.rollback()
            raise e
