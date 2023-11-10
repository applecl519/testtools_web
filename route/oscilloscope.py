from utils.SiglentDevices import SDS5034
from flask import Blueprint, jsonify, request

oscilloscope_bp = Blueprint('oscilloscope', __name__)


# 示波器 routes
@oscilloscope_bp.route('/connect/<ip>', methods=['GET'])
def connect(ip):
    global handler
    try:
        handler = SDS5034(ip)
        if handler:
            return jsonify(result='Connection Successful')
        else:
            return jsonify(result='Connection Failed')
    except Exception:
        return jsonify(result='Connection Failed')


# API routes
@oscilloscope_bp.route('/run', methods=['GET'])
def api_run():
    result = handler.run()
    return jsonify(result=result)


# API routes
@oscilloscope_bp.route('/stop', methods=['GET'])
def api_stop():
    result = handler.stop()
    return jsonify(result=result)


@oscilloscope_bp.route('/get_time_scale', methods=['GET'])
def api_get_time_scale():
    result = handler.get_time_scale()
    return jsonify(result=result)


@oscilloscope_bp.route('/set_time_scale', methods=['POST'])
def api_set_time_scale():
    data = request.json
    scale = float(data['scale'])
    # scale = float(request.form['scale'])
    result = handler.set_time_scale(scale)
    return jsonify(result=result)


# 自动调整
is_running = False


def your_while_loop_function(direction):
    # 调用 api_get_time_scale 函数并获取其返回值
    response = api_get_time_scale()
    data = response.get_json()  # 获取 JSON 数据
    current_s = data['result']  # 获取具体的返回值
    print(current_s)
    mv = [
        0.00005, 0.00002, 0.00001, 0.0005, 0.0002, 0.0001, 0.005, 0.002, 0.001,
        0.05, 0.02, 0.01, 0.5, 0.2, 0.1
    ]
    index = mv.index(current_s)
    if direction == 'left':
        if index > 0:
            current_ss = mv[index - 1]
            print(current_ss)
            handler.set_time_scale(scale=current_ss)
    elif direction == 'right':
        if index < len(mv) - 1:
            current_ss = mv[index + 1]  # index = mv.index(current_s)
            print(current_ss)
            handler.set_time_scale(scale=current_ss)


@oscilloscope_bp.route('/leftmv')
def leftmv():
    global is_running
    is_running = True
    your_while_loop_function('left')
    return jsonify(status='success')


@oscilloscope_bp.route('/stopmv')
def stopmv():
    global is_running
    is_running = False
    return jsonify(status='success')


@oscilloscope_bp.route('/rightmv')
def rightmv():
    global is_running
    is_running = True
    your_while_loop_function('right')
    return jsonify(status='success')


@oscilloscope_bp.route('/get_ch_offset', methods=['GET'])
def api_get_ch_offset():
    ch = request.args.get('ch')
    result = handler.get_ch_offset(ch)
    return jsonify(result=result)


@oscilloscope_bp.route('/set_ch_offset', methods=['POST'])
def api_set_ch_offset():
    ch = int(request.form['ch'])
    offset = float(request.form['offset'])
    result = handler.set_ch_offset(ch, offset)
    return jsonify(result=result)


@oscilloscope_bp.route('/get_measurement', methods=['GET'])
def get_measurement():
    pos = request.args.get('pos')
    temp_result = handler.get_measurement_item_value(pos)
    # result = float(temp_result)
    result = format(float(temp_result), ".8f")
    print(result)
    return jsonify(result=result)


@oscilloscope_bp.route('/setscreenshot', methods=['POST'])
def set_screenshot():
    try:
        data = request.json
        phname = data['name']
        result = handler.get_screenshot(na=phname)
        return jsonify(result='sc')
    except Exception as e:
        pass