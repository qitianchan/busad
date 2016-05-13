# -*- coding: utf-8 -*-
from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with
from flask_restful import Resource
import flask_restful as restful
from server.app.extensions import db, bcrypt, auth
from server.app.models import Route, Bus
from  sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
route_fields = {
    'id': fields.Integer,
    'district_id': fields.Integer,
    'route_name': fields.String,
}

district_parser = reqparse.RequestParser()

district_parser.add_argument(
    'district_name', dest='districName',
    type=str, location='form',
    required=True, help='The district name'
)


class RouteList(Resource):
    decorators = [auth.login_required]

    @marshal_with(route_fields)
    def get(self):
        routes = Route.get_routes()
        # if not routes:
        #     abort(404)
        return routes

    @marshal_with(route_fields)
    def post(self):
        district_id = request.json.get('district_id')
        route_name = request.json.get('route_name')
        if not route_name:
            abort(422)

        route = Route(district_id, route_name)
        db.session.add(route)
        db.session.commit()
        return route


class RouteAPI(Resource):
    decorators = [auth.login_required, marshal_with(route_fields)]

    # @marshal_with(route_fields)
    def get(self, id):
        route = Route.get(id)
        if not route:
            abort(404)
        return route


    def put(self, id):
        district_id = request.json.get('district_id')
        route_name = request.json.get('route_name')
        route = Route.get(id)
        if not route:
            abort(404)
        route.district_id = district_id
        route.route_name = route_name

        db.session.add(route)
        db.session.commit()

        return route, 201

    @auth.login_required
    def delete(self, id):
        route = Route.get(id)
        if route:
            try:
                Route.delete(id)
                return jsonify({'success': u'删除成功'})
            except IntegrityError, e:
                response = jsonify({'error': u'存在引用的外鍵'})
                response.status_code = 422
            # if delete failed
            # if not Route.get(id):
            #     return jsonify({'success': u'删除成功'})
            # response = jsonify({'error': u'存在引用的外鍵'})
            # response.status_code = 422
            # return response
        else:
            response = jsonify({'error': u'该路线不存在'})
            response.status_code = 404
            return response
