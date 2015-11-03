# -*- coding: utf-8 -*-
from server.app.extensions import auth, bcrypt
from flask_restful import Resource
from flask import request, jsonify
from flask_restful import fields
import os

class Publish(Resource):

    # TODO:文件接收
    def post(self):
        f = request.files['file']
        euis = request.form.get('euis')
        if euis:
            euis = euis.split(',')
            # TODO
            self._send_file(euis, f)
            # f.save(f.filename)

            return '上传成功', 201
        else:
            return '', 300

    def _send_file(self, euis, file):
        #   TODO: 发送文件到
        while(True):
            chunk = file.read(50)
            if not chunk:
                break

            # todo: 传输到设备
            for eui in euis:
                print eui, ':', chunk.encode('hex')

