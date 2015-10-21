# -*- coding: utf-8 -*-
from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with
from flask_restful import Resource
import flask_restful as restful
from server.app.extensions import db, bcrypt, auth
from server.app.models import District
from  sqlalchemy import and_
from sqlalchemy.exc import IntegrityError


district_fields = {
    'id': fields.Integer,
    'district_name': fields.String
}

district_parser = reqparse.RequestParser()

district_parser.add_argument(
    'district_name', dest='districName',
    type=str, location='form',
    required=True, help='The district name'
)


class DistrictAPI(Resource):
    decorators = [auth.login_required]

    @marshal_with(district_fields)
    def get(self):
        current_user = g.user
        districts = District.get_district_list()
        return districts

    # @marshal_with(district_fields)
    def post(self):
        district_name = request.json.get('district_name')
        if not district_fields:
            abort(400)

        district = District(district_name=district_name)
        try:
            db.session.add(district)
            db.session.commit()
            return marshal(district, district_fields), 201
        except IntegrityError, e:
            db.session.rollback()
            return jsonify({'resCode': '31', 'resMsg': u'区域名已经存在'})

    @marshal_with(district_fields)
    def put(self, id):
        district = District.get(id)
        if not district:
            abort(400)

        district_name = request.json.get('district_name')
        district.update_distrct(district_name)
        db.session.add(district)
        db.session.commit()

        return district, 201

    @marshal_with(district_fields)
    def delete(self, id):
        district = District.get(id)
        if district:
            if district.routes:
                return jsonify({'resCode': '30', 'resMsg': 'theere is some routes index for it'})
            else:
                db.session.delete(district)
                db.session.commit()
                return District.get_district_list()

        else:
            return jsonify({"resCode": '30', 'resMsg': 'District is not exit'})

