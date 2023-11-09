from flask import Blueprint, jsonify, request
import pyvisa as visa

itech_bp = Blueprint('itech', __name__)


@itech_bp.route('/connect/<visas>', methods=['GET'])
def itech_connect(visas):
    global instrument
    try:
        rm = visa.ResourceManager()
        instrument = rm.open_resource(visas)
        if instrument:
            return jsonify(result='Connection Successful')
        else:
            return jsonify(result='Connection Failed')
    except Exception:
        return jsonify(result='Connection Failed')


@itech_bp.route('/power_on', methods=['GET'])
def itech_on():
    try:
        command = 'OUTPut on'
        response = instrument.write(command)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')


@itech_bp.route('/power_off', methods=['GET'])
def itech_off():
    try:
        command = 'OUTPut off'
        response = instrument.write(command)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')


@itech_bp.route('/setAV', methods=['POST'])
def itech_setAV():
    try:
        Vn = int(request.form['voltage'])
        An = int(request.form['current'])
        command = f'APPLy {Vn},{An}'
        response = instrument.write(command)
        return jsonify(result='Connection Successful')
    except Exception as e:
        print('1', e)
        return jsonify(result='Connection Failed')