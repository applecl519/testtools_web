import threading
from pydasrmt.Command.CmdGeneratorCan import *


def send_can_messages(channel, id, b0='0', b1='0', b2='0', b3='0', b4='0', b5='0', b6='0', b7='0'):
    cmd = CmdGeneratorCan()
    # cmd.enableFlowCan(True)
    cmd.initSocket('127.0.0.1', 6667, 6666)
    cmd.setChannelNode(channel, 1)
    cmd.setParamCan(500, 2, 1, 1)
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



def send_can_messages_loop(channel, id, b0='0', b1='0', b2='0', b3='0', b4='0', b5='0', b6='0', b7='0'):
    try:
        global is_looping
        is_looping = True
        def send_message():
            if is_looping:
                cmd = CmdGeneratorCan()
                cmd.initSocket('127.0.0.1', 6667, 6666)
                cmd.setChannelNode(channel, 1)
                cmd.setParamCan(500, 2, 1, 1)
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


def receive_can_messages(cmd):
    cmd.enableFlowCan(True)

    try:
        while True:
            received_message = cmd.receiveCanMessage(canID=int('200', 16))

            if received_message is not None:
                print("Received CAN message:", received_message)
                print('data~~~~~~~', received_message.Header.Data, type(received_message.Header.Data))
                print('id~~~~~~~~~', format(int(received_message.ID), 'x'))
                hex_list = [hex(byte) for byte in received_message.Header.Data]
                print(hex_list)
    except Exception as e:
        print("Error receiving CAN message:", e)


def sCan(ip, portPub, portSub):
    cmd = CmdGeneratorCan()
    cmd.initSocket(ip, portPub, portSub)
    cmd.setChannelNode(3, 1)

    # send_thread = threading.Thread(target=send_can_messages_loop, args=(cmd,))
    receive_thread = threading.Thread(target=receive_can_messages, args=(cmd,))

    # send_thread.start()
    receive_thread.start()


if __name__ == '__main__':
    ip = "127.0.0.1"
    portPub = 6667
    portSub = 6666
    sCan(ip, portPub, portSub)
    # send_can_messages(channel=3,id='500',b0='1')