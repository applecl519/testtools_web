from flask import Blueprint, jsonify, request
import requests

relaytronix_bp = Blueprint('relay', __name__)


@relaytronix_bp.route('/connect', methods=['GET'])
def tek_connect():
    try:
        command = request.args.get('command')
        tem_url = request.args.get('url')
        url = "http://" + tem_url.strip('\'"') + "?command=" + command.strip('\'"')
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        if response:
                return jsonify(result='Connection Successful')
        else:
            return jsonify(result='Connection Failed')
    except Exception as e:
        return jsonify(result='Connection Failed', error=str(e))
