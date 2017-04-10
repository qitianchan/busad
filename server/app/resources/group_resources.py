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
from server.app.resources.sendfile.send_file import GroupSender
import threading

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from server.app.utils import MSocketIO, EventNameSpace
from server.app.config import OURSELF_APP_EUI, OURSELF_TOKEN, OURSELF_HOST, OURSELF_PORT
import random
LORA_HOST = OURSELF_HOST
APP_EUI = OURSELF_APP_EUI
TOKEN = OURSELF_TOKEN
LORA_PORT = OURSELF_PORT
NAMESPACE = '/test'

# socketio_cli = MSocketIO(LORA_HOST, LORA_PORT, EventNameSpace, params={'app_eui': APP_EUI, 'token': TOKEN})
#
# event_space = socketio_cli.define(EventNameSpace, path=NAMESPACE)

group_fields = {
    'id': fields.Integer,
    'group_name': fields.String,
    'group_id': fields.String,
    'eui': fields.String
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
        group_id = request.json.get('group_id')
        group_eui = request.json.get('group_eui')
        if not group_name:
            abort(422)

        def group_eui_productor():
            import random
            s = ''
            for i in range(4):
                s += chr(random.randint(0, 255))
            return s.encode('hex').upper()

        def on_add_group(data):
            pass

        # group_eui = group_eui_productor()

        # socketio_cli = MSocketIO(LORA_HOST, LORA_PORT, EventNameSpace, params={'app_eui': APP_EUI, 'token': TOKEN})
        #
        # event_space = socketio_cli.define(EventNameSpace, path=NAMESPACE)

        # event_space.emit('add_group', {'name': group_name, 'group_addr': group_eui, 'nwkskey': '2B7E151628AED2A6ABF7158809CF4F3C',
        #                                'appskey': '2B7E151628AED2A6ABF7158809CF4F3C'})
        # socketio_cli.wait(3)

        group = Group(group_name, group_id, group_eui)
        # todo 添加到LoRaWan服务器，带回group_id
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
            b['bus_eui'] = bus.eui
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
                    buses.append({'route_id': bus.route_id, 'bus_name': bus.plate_number, 'bus_id': bus.id, 'in_group': in_group,
                                  'bus_eui': bus.eui})
            data['buses'] = buses
            res.append(data)
        return jsonify({'buses_all': res, 'in_group': buses_in_group_res})

    @auth.login_required
    @marshal_with(group_fields)
    def put(self, id):
        group_name = request.json.get('group_name')
        group = Group.get(id)
        if not group:
            abort(404)
        group.group_name = group_name
        # todo: 添加组到LoRa服务器
        # group_eui = None

        group.save()
        return group

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
        failed_rm_euis = []
        failed_add_euis = []

        if group.group_id:
            original_members = group.buses
            for bus in original_members:
                if bus.id not in [mem['bus_id'] for mem in members]:
                    delete.append(bus.id)

            for m in members:
                if m['bus_id'] not in [ori.id for ori in original_members]:
                    add.append(m['bus_id'])

            # delete members
            delete_buses = []
            for d in delete:
                bus = Bus.get(d)
                if bus:
                    delete_buses.append(bus)
             # add members
            add_buses = []
            for a in add:
                bus = Bus.get(a)
                if bus:
                    add_buses.append(bus)

            # 写入数据库
            for bus in delete_buses:
                if bus.eui not in failed_rm_euis:
                    bus.group_id = None
                    db.session.add(bus)
            for bus in add_buses:
                if bus.eui.upper() not in failed_add_euis:
                    bus.group_id = group.id
                    db.session.add(bus)
            db.session.commit()

            error_message = ''
            if failed_add_euis + failed_rm_euis:
                error_message = ', '.join(failed_add_euis + failed_rm_euis) + ' 操作失败'
            return {'error_message': error_message}, 201

        return {'error_message': '组不存在'}, 422


def filter_buses(buses, route_id):
    res = []
    for bus in buses:
        if bus.route_id == route_id:
            res.append(bus)
    return res


def add_group_to_lora_wan_server(group_eui, group_name):
    # todo: 添加组到loraWAN
    pass


class GroupUpload(Resource):

    def post(self):
        print('hello, GroupUpload')
        content = request.files['file'].read()
        group_id = request.form['group_id']
        user_id = request.form['user_id']
        group = Group.get_by_groupid(group_id)

        if group:
            dev_euis = Bus.get_euis_by_group_id(group.id, user_id=user_id)
            if dev_euis:
                sender = GroupSender(content, group_id, dev_euis, package_length=40)
                #todo: 发送线程
                # new_thread = threading.Thread(target=send_file_with_timelimit, args=(chunks, euis, progress_code, last_progress_code))

                # try:
                #     new_thread.start()
                # except Exception, e:
                #     print '*' * 120
                #     print e.message

                success = sender.send()

        return 'dsf'



if __name__ == '__main__':
    APP_EUI = 'BB7A000000000032'
    TOKEN = '-YAN0Up6nMvbTMre0rdoHg'
    socketio_cli = MSocketIO(LORA_HOST, LORA_PORT, EventNameSpace, params={'app_eui': APP_EUI, 'token': TOKEN})
    event_space = socketio_cli.define(EventNameSpace, path=NAMESPACE)
    event_space.emit('add_dev_into_group', {'group_id': '0000CBF1', 'cmd': 'add_dev_into_group',
                                                        'dev_eui': 'BE00000000000013'})
    print('done!')
    # event_space.emit('')