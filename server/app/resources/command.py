# -*- coding: utf-8 -*-
from flask_restful import Resource
from flask import Blueprint, jsonify, request
from server.app.resources.sendfile.send_file import OpenLightCommandSender, CloseLightCommandSender, RssiTestCommandSender,\
    UpLoadCommandSender, UpLoadCommandSender_2

from server.app.utils import MSocketIO, EventNameSpace
command = Blueprint('command', __name__)

@command.route('/openpower', methods=["POST"])
def open_power():
    eui = request.json.get('bus_eui').strip().upper()
    open_sender = OpenLightCommandSender(eui)
    success = open_sender.send()
    if success:
        return jsonify({'code': '2000', 'message': 'open power success'})
    else:
        response = jsonify({'success': False, 'message': 'open power failed'})
        response.status_code = 422
        return response


@command.route('/closepower', methods=['POST'])
def close_power():
    eui = request.json.get('bus_eui').strip().upper()
    close_sender = CloseLightCommandSender(eui)
    success = close_sender.send()
    if success:
        return jsonify({'success': True, 'message': 'close power success'})
    else:
        response = jsonify({'success': False, 'message': 'close power failed'})
        response.status_code = 422
        return response


@command.route('/rssitest', methods=['POST'])
def rssi_test():
    eui = request.json.get('bus_eui').strip().upper()
    sender = RssiTestCommandSender(eui)
    success = sender.send()
    if success:
        return jsonify({'success': True, 'message': 'rssi test success'})
    else:
        response = jsonify({'success': False, 'message': 'rssi test failed'})
        response.status_code = 422
        return response

@command.route('/uploadmessage', methods=['POST'])
def upload_message():
    eui = request.json.get('bus_eui').strip().upper()
    sender = UpLoadCommandSender(eui)
    success = sender.send()
    if success:
        return jsonify({'success': True, 'message': 'Upload message 1 success'})
    else:
        response = jsonify({'success': False, 'message': 'Upload message 1 failed'})
        response.status_code = 422
        return response


@command.route('/uploadmessage2', methods=['POST'])
def upload_message2():
    eui = request.json.get('bus_eui').strip().upper()
    sender = UpLoadCommandSender_2(eui)
    success = sender.send()
    if success:
        return jsonify({'success': True, 'message': 'Upload message 2 success'})
    else:
        response = jsonify({'success': False, 'message': 'Upload message 2 failed'})
        response.status_code = 422
        return response