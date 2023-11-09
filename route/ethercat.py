# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from fabric import Connection

ethercat_bp = Blueprint('ethercat', __name__)


@ethercat_bp.route('/sent', methods=['POST'])
def ethercat_sent():
    try:
        data = request.json
        host = data['ip']
        username = data['user']
        password = data['passwd']
        command = data['command']
        match_line = data['mastr']
        result = ""
        if request.method == 'POST':
            try:
                with Connection(host=host,
                                user=username,
                                connect_kwargs={'password': password}) as c:
                    result = c.run(command, hide=True).stdout
                    if match_line:
                        result = filter_result(result, match_line)
            except Exception as e:
                result = f"An error occurred: {str(e)}"

        return jsonify(result=result)
    except Exception as e:
        return jsonify(result='send Failed')


def filter_result(result, match_lines):
    lines = result.split('\n')
    match_lines = match_lines.split('&')
    filtered_lines = []
    for line in lines:
        for match_line in match_lines:
            if match_line in line:
                filtered_lines.append(line)
                break
    return '\n'.join(filtered_lines)


@ethercat_bp.route('/upload', methods=['POST'])
def ethercat_upload_file():
    try:
        # Handle the uploaded file here (e.g., save it or process it)
        uploaded_file = request.files['file']

        if uploaded_file:
            # Save the uploaded file to the server or process it
            # You can use libraries like Paramiko to send the file to a remote server

            # Return a response
            return jsonify(result="文件上传成功")

    except Exception as e:
        return jsonify(result='文件上传失败')
