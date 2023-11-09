from flask import Blueprint, jsonify, request
import pyvisa as visa
from utils.signal_generator_devices import tektronix_func_gen as tfg

tektronix_bp = Blueprint('tek', __name__)


@tektronix_bp.route('/connect', methods=['GET'])
def tek_connect():
    try:
        visas = request.args.get('visa')
        if visas:
            rm = visa.ResourceManager()
            instrument_tek = rm.open_resource(visas)
            if instrument_tek:
                return jsonify(result='Connection Successful')
            else:
                return jsonify(result='Connection Failed')
        else:
            return jsonify(result='Invalid VISA address')
    except Exception as e:
        return jsonify(result='Connection Failed', error=str(e))


@tektronix_bp.route('/setbotepl', methods=['POST'])
def tek_set_botepl():
    try:
        data = request.json
        pl = data['pl']
        bote = int(data['bote'].split('%')[0])
        ch1_check = data['channel1']
        ch2_check = data['channel2']
        ch1_check = "true" if ch1_check else "false"
        ch2_check = "true" if ch2_check else "false"
        visas = data['visa']
        numeric_part = ''.join(filter(str.isdigit, pl))
        letter_part = ''.join(filter(str.isalpha, pl))
        instrument_tek = tfg.FuncGen(visas)
        if ch1_check and not ch2_check:
            instrument_tek.ch1.set_frequency(float(numeric_part),
                                             unit=str(letter_part))
            instrument_tek.ch1.set_duty(bote)
        elif ch2_check and not ch1_check:
            instrument_tek.ch2.set_frequency(float(numeric_part),
                                             unit=str(letter_part))
            instrument_tek.ch2.set_duty(bote)
        elif ch1_check and ch2_check:
            instrument_tek.ch1.set_frequency(float(numeric_part),
                                             unit=str(letter_part))
            instrument_tek.ch1.set_duty(bote)
            instrument_tek.ch2.set_frequency(float(numeric_part),
                                             unit=str(letter_part))
            instrument_tek.ch2.set_duty(bote)
        instrument_tek.close()
        return jsonify(result='Connection Successful')
    except Exception as e:
        return jsonify(result='Connection Failed')
