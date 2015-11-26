# -*- coding: utf-8 -*-
from flask import request, jsonify
from flask_restful import Resource, fields, marshal, reqparse, marshal_with
from server.app.extensions import auth
from redis import Redis
from server.app.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB, REDIS_URL


class Progress(Resource):
    def get(self, progress_code):
        r = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)

        if not progress_code:
            response = jsonify({'error': 'progress_code is none'})
            response.status_code = 422
            return response
        if not r.ping():
            response = jsonify({'error': 'redis connection error'})
            response.status_code = 422
            return response

        progress = r.get(progress_code)
        return jsonify({'progress': progress or 0})

if __name__ == '__main__':

    r = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
    print r.ping()
