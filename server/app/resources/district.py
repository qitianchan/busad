# -*- coding: utf-8 -*-
from flask import g, request, abort, jsonify, url_for
from flask_restful import fields, marshal, reqparse, marshal_with
from flask_restful import Resource
from server.app.extensions import db, bcrypt, auth
from server.app.models import District
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


class District_Resource(Resource):
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
            res = jsonify({'resCode': '31', 'resMsg': u'区域名已经存在'})
            res.status_code = 422
            return res




class DistrictAPI(Resource):

    @marshal_with(district_fields)
    def delete(self, id):
        district = District.get(id)
        if district:
            # if district.routes:
            #     res = jsonify({'error': 'theere is some routes index for it'})
            #     res.status_code = 422
            #     return res
            # else:
            #     db.session.delete(district)
            #     db.session.commit()
            #     return District.get_district_list()
            db.session.delete(district)
            db.session.commit()
        else:
            return jsonify({"resCode": '30', 'resMsg': 'District is not exit'})

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