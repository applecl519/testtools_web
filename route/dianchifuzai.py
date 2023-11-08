from flask import Blueprint, jsonify, request
import pyvisa as visa

dianchifuzai_bp = Blueprint('dianchifuzai', __name__)


@dianchifuzai_bp.route('/connect', methods=['GET'])
def dianchifuzai_connect():
    global instrument
    try:
        visas = request.args.get('visa')
        if visas:
            rm = visa.ResourceManager()
            instrument = rm.open_resource(visas)
            if instrument:
                return jsonify(result='Connection Successful')
            else:
                return jsonify(result='Connection Failed')
        else:
            return jsonify(result='Invalid VISA address')
    except Exception as e:
        return jsonify(result='Connection Failed', error=str(e))

@dianchifuzai_bp.route('/power_on', methods=['GET'])
def dianchifuzai_on():
    try:
        command = 'INP 1'
        response = instrument.write(command)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')


@dianchifuzai_bp.route('/power_off', methods=['GET'])
def dianchifuzai_off():
    try:
        command = 'INP 0'
        response = instrument.write(command)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')


@dianchifuzai_bp.route('/changelocal', methods=['GET'])
def dianchifuzai_changelocal():
    try:
        command = 'SYST:LOC'
        response = instrument.write(command)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')

@dianchifuzai_bp.route('/changermt', methods=['GET'])
def dianchifuzai_changermt():
    try:
        command = 'SYST:RWL'
        response = instrument.write(command)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')



@dianchifuzai_bp.route('/Screen', methods=['GET'])
def dianchifuzai_Screen():
    try:
        commandv = 'FETC:VOLT?'#屏幕显示电压
        commanda = 'FETC:CURR?'#屏幕显示电流
        responsev = instrument.query(commandv).strip()
        responsea = instrument.query(commanda).strip()
        result = f"{responsev}V;{responsea}A"
        return jsonify(result=result)
    except Exception:
        return jsonify(result='Connection Failed')

@dianchifuzai_bp.route('/setVoltage', methods=['POST'])
def dianchifuzai_setVoltage():
    try:
        dianchifuzai_V = int(request.form['voltage'])
        commandv = 'FUNC VOLTage'#屏幕显示电压
        commanda = f'VOLT {dianchifuzai_V}'#屏幕显示电流
        responsev = instrument.write(commandv)
        responsea = instrument.write(commanda)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')


@dianchifuzai_bp.route('/setCurrent', methods=['POST'])
def dianchifuzai_setCurrent():
    try:
        dianchifuzai_V = int(request.form['current'])
        commandvs = 'FUNC CURRent'
        commandas = f'CURR {dianchifuzai_V}'
        responsev = instrument.write(commandvs)
        responsea = instrument.write(commandas)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')


@dianchifuzai_bp.route('/setResistance', methods=['POST'])
def dianchifuzai_setResistance():
    try:
        dianchifuzai_R = int(request.form['resistance'])
        commandvs = 'FUNC RESistance'
        commandas = f'RES {dianchifuzai_R}'
        responsev = instrument.write(commandvs)
        responsea = instrument.write(commandas)
        return jsonify(result='Connection Successful')
    except Exception:
        return jsonify(result='Connection Failed')