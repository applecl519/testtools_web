from flask import Blueprint, jsonify, request,send_file
from utils.vcardas.sendandrecv import *
import threading
import subprocess
from func_timeout import FunctionTimedOut


vcardas_bp = Blueprint('vcardas', __name__)

is_looping = False
@vcardas_bp.route('/sent', methods=['POST'])
def vcardas_sent():
    global is_looping
    try:
        data = request.json
        channel = int(data['channel'])
        id = data['can_id']
        b0 = data['bit0']
        b1 = data['bit1']
        b2 = data['bit2']
        b3 = data['bit3']
        b4 = data['bit4']
        b5 = data['bit5']
        b6 = data['bit6']
        b7 = data['bit7']
        is_looping = data['isLoop']
        cmd = CmdGeneratorCan()
        cmd.initSocket('127.0.0.1', 6667, 6666)
        cmd.setChannelNode(channel, 1)
        cmd.setParamCan(500, 0, 1, 1)

        if not is_looping:
            try:
                cmd.sendCan(CanCmd.EFrameStatus.Can, bytes([int(b0, 16),
                                                            int(b1, 16),
                                                            int(b2, 16),
                                                            int(b3, 16),
                                                            int(b4, 16),
                                                            int(b5, 16),
                                                            int(b6, 16),
                                                            int(b7, 16)]), int(id, 16))
            except Exception as e:
                print("Error sending CAN message:", e)
            return jsonify(result='send Successful')
        else:
            try:
                # is_looping = True
                def send_message():
                    if is_looping:
                        cmd.sendCan(CanCmd.EFrameStatus.Can, bytes([int(b0, 16),
                                                                    int(b1, 16),
                                                                    int(b2, 16),
                                                                    int(b3, 16),
                                                                    int(b4, 16),
                                                                    int(b5, 16),
                                                                    int(b6, 16),
                                                                    int(b7, 16)]), int(id, 16))
                        # 继续下一次循环
                        if is_looping:
                            threading.Timer(0, send_message).start()  # 使用 threading.Timer 来模拟异步操作

                # 启动第一次循环
                send_message()
            except Exception as e:
                print("Error sending CAN message:", e)
            return jsonify(result='Loop Started')
    except Exception as e:
        return jsonify(result='send Failed')


@vcardas_bp.route('/stop_loop', methods=['POST'])
def vcardas_stop_loop():
    global is_looping
    is_looping = False
    return jsonify(result='Loop Stopped')



@vcardas_bp.route('/recv', methods=['POST'])
def vcardas_recv():
    global is_looping
    data = request.json
    channel = int(data['channel'])
    id = data['can_id']
    b0 = data['bit0']
    b1 = data['bit1']
    b2 = data['bit2']
    b3 = data['bit3']
    b4 = data['bit4']
    b5 = data['bit5']
    b6 = data['bit6']
    b7 = data['bit7']
    is_looping = data['isLoop']
    cmd = CmdGeneratorCan()
    cmd.initSocket('127.0.0.1', 6667, 6666)
    cmd.setChannelNode(channel, 1)
    cmd.enableFlowCan(True)
    cmd.setParamCan(500, 0, 1, 1)
    received_message = None
    try:
        while received_message is None:
            received_message = cmd.receiveCanMessage(canID=int(id, 16))
        hex_list = [hex(byte) for byte in received_message.Header.Data]
        if b0 == b1 == b2 == b3 == b4 == b5 == b6 == b7 == '0':
            return jsonify(result=hex_list)
        else:
            for i in range(8):
                # print(f'0x{f"b{i}"}', hex_list[i])
                if hex_list[i] == f'0x{eval(f"b{i}")}':
                    return jsonify(result=hex_list)
        return jsonify(result=["没有匹配消息"])
    except func_timeout.FunctionTimedOut as e:
            return jsonify(result=["总线无消息"])


