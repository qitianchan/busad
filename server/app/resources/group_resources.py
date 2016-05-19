# -*- coding: utf-8 -*-
from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with
from flask_restful import Resource
import flask_restful as restful
from server.app.extensions import db, bcrypt, auth
from server.app.models import Group, Bus, Route
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from json import dumps, loads
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from server.app.utils import MSocketIO, EventNameSpace
from server.app.config import OURSELF_APP_EUI, OURSELF_TOKEN, OURSELF_HOST, OURSELF_PORT

LORA_HOST = OURSELF_HOST
APP_EUI = OURSELF_APP_EUI
TOKEN = OURSELF_TOKEN
LORA_PORT = OURSELF_PORT
NAMESPACE = '/test'

socketio_cli = MSocketIO(LORA_HOST, LORA_PORT, EventNameSpace, params={'app_eui': APP_EUI, 'token': TOKEN})

event_space = socketio_cli.define(EventNameSpace, path=NAMESPACE)

group_fields = {
    'id': fields.Integer,
    'group_name': fields.String,
}

group_parser = reqparse.RequestParser()

group_parser.add_argument(
    'group_name', dest='groupName',
    type=str, location='form',
    required=True, help='The group name'
)


class GroupList(Resource):
    decorators = [auth.login_required]

    @auth.login_required
    @marshal_with(group_fields)
    def get(self):
        groups = Group.get_groups()
        # if not routes:
        #     abort(404)
        return groups

    @auth.login_required
    @marshal_with(group_fields)
    def post(self):
        group_name = request.json.get('group_name')
        if not group_name:
            abort(422)

        group = Group(group_name)
        db.session.add(group)
        db.session.commit()
        return group


class GroupAPI(Resource):
    decorators = [auth.login_required]

    def get(self, id):
        buses_in_group = Bus.query.filter(and_(Bus.user_id == g.user.id, Bus.group_id == id)).all()
        buses_in_group_res = []
        for bus in buses_in_group:
            b = dict()
            b['route_id'] = bus.route_id
            b['bus_name'] = bus.plate_number
            b['bus_id'] = bus.id
            buses_in_group_res.append(b)

        routes = Route.get_routes()
        buses_all = Bus.get_all()
        res = []
        for route in routes:
            data = {}
            data['route_id'] = route.id
            data['route_name'] = route.route_name
            buses = []
            for bus in buses_all:
                if bus.route_id == route.id:
                    in_group = bus.group_id == id
                    buses.append({'route_id': bus.route_id, 'bus_name': bus.plate_number, 'bus_id': bus.id, 'in_group': in_group})
            data['buses'] = buses
            res.append(data)
        return jsonify({'buses_all': res, 'in_group': buses_in_group_res})

    @auth.login_required
    def put(self, id):
        group_name = request.json.get('group_name')
        group = Group.get(id)
        if not group:
            abort(404)
        group.group_name = group_name
        group.save()
        return group, 201

    @auth.login_required
    def delete(self, id):
        group = Group.get(id)
        if group:
            try:
                group.remove()
                return jsonify({'success': u'删除成功'})
            except IntegrityError, e:
                response = jsonify({'error': u'删除失败'})
                response.status_code = 422
        else:
            response = jsonify({'error': u'该组不存在'})
            response.status_code = 404
            return response


class GroupMember(Resource):
    decorators = [auth.login_required]

    def get(self, group_id):
        return {'message': 'success'}, 201

    def put(self, group_id):
        group = Group.get(group_id)
        members = loads(request.data)
        delete = []
        add = []
        if group:
            original_members = group.buses
            for bus in original_members:
                if bus.id not in [mem['bus_id'] for mem in members]:
                    delete.append(bus.id)

            for m in members:
                if m['bus_id'] not in [ori.id for ori in original_members]:
                    add.append(m['bus_id'])

            # delete members
            for d in delete:
                pass
            # add members
            return {'message': 'success'}, 201
        return {'message': '组不存在'}, 422


def filter_buses(buses, route_id):
    res = []
    for bus in buses:
        if bus.route_id == route_id:
            res.append(bus)
    return res


