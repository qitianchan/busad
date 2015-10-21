# -*- coding: utf-8 -*-
from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with
from flask_restful import Resource
import flask_restful as restful
from server.app.extensions import db, bcrypt, auth
from server.app.models import Route
from  sqlalchemy import and_


route_fields = {
    'id': fields.Integer,
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
        routes = Route.query.filter(and_(Route.user_id == g.user.id)).all()
        if not routes:
            abort(404)
        return {}


class RouteAPI(Resource):
    decorators = [auth.login_required, marshal_with(route_fields)]

    # @marshal_with(route_fields)
    def get(self, id):
        route = Route.get(id)
        if not route:
            abort(404)
        return route

    def post(self):
        district_id = request.json.get('districtId')
        route_name = request.json.get('routeName')
        if not route_name or district_id:
            abort(400)

        route = Route(district_id, route_name)
        db.session.add(route)
        db.session.commit()
        return route, 201.

    def put(self, id):
        district_id = request.json.get('districtId')
        route_name = request.json.get('routeName')
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
            if route.buses:
                return jsonify({'resCode': '30', 'resMsg': 'theere is some buses index for it'})
            else:
                db.session.delete(route)
                db.session.commit()
                return jsonify({"resCode": '20', 'resMsg': 'delete success'})

        else:
            return jsonify({"resCode": '30', 'resMsg': 'route is not exit'})

