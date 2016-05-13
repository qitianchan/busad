# -*- coding: utf-8 -*-
from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with
from flask_restful import Resource
import flask_restful as restful
from server.app.extensions import db, bcrypt, auth
from server.app.models import Group
from  sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

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
    decorators = [auth.login_required, marshal_with(group_fields)]

    def get(self, id):
        route = Group.get(id)
        if not route:
            abort(404)
        return route

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
