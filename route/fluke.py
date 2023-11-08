from flask import Blueprint, jsonify
import pyvisa as visa

fluke_bp = Blueprint('fluke', __name__)


@fluke_bp.route('/connect/<visas>', methods=['GET'])
def fluke_connect(visas):
    global instrument_fluke
    try:
        rm = visa.ResourceManager()
        instrument_fluke = rm.open_resource(visas)
        if instrument_fluke:
            return jsonify(result='Connection Successful')
        else:
            return jsonify(result='Connection Failed')
    except Exception:
        return jsonify(result='Connection Failed')
    finally:
        instrument_fluke.close()


def getsignvalue(sigvalue):
    try:
        scientific_notation_str = sigvalue
        # 将科学计数法字符串转换为十进制数值
        decimal_value = float(scientific_notation_str)
        return decimal_value
    except ValueError as e:
        return '0'


@fluke_bp.route('/query/<visas>', methods=['GET'])
def fluke_query(visas):
    try:
        rm = visa.ResourceManager()
        instrument_fluke = rm.open_resource(visas)
        command = 'MEAS?'
        response = instrument_fluke.query(command)
        rs = response.split(' ')
        result = f'{getsignvalue(rs[0])} {rs[1]}'
        return jsonify(result=result)
    except Exception as e:
        print(e)
        return jsonify(result='Connection Failed')
