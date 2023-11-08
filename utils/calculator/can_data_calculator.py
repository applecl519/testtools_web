from collections import OrderedDict
from crc_calculator import *

sign_opencircuit_unshortcircuit = ['0', '0', '1']
sign_opencircuit_shortcircuit_to_ccv = ['0', '1', '1']
sign_opencircuit_shortcircuit_to_gnv = ['0', '1', '0']
default_channle = ['0', '0', '0']
sign_open_shortcircuit_to_ccv = ['1', '0', '1']
sign_open_shortcircuit_to_gnv = ['1', '0', '0']
sign = {
    '1': sign_opencircuit_unshortcircuit,
    '3': sign_opencircuit_shortcircuit_to_ccv,
    '2': sign_opencircuit_shortcircuit_to_gnv,
    '0': default_channle,
    '5': sign_open_shortcircuit_to_ccv,
    '4': sign_open_shortcircuit_to_gnv
}
mfiu_crc_list = []


def result_bytes(num, byte_example, choose_card='1'):
    if choose_card == '1' or choose_card == '3':
        byte_example_str = ''.join(byte_example)
        stop_index = None
        for i, c in enumerate(byte_example_str):
            if c == '1':
                stop_index = i
        if stop_index is not None:
            f = byte_example_str[:stop_index] + '1'
            byte1 = f[::-1]
            hex_num = hex(int(byte1, 2))[2:]
            if choose_card == '1':
                if num <= 6:
                    print(f'CAN ID 100   CAN DATA ：第{num}个字节为： {hex_num} \n')
                    # autovcardas(num, hex_num)
                elif num > 6:
                    print(f'CAN ID 101   CAN DATA ：第{num - 6}个字节为：{hex_num} \n')
                    # autovcardas(num-6, hex_num)
            else:
                print(f'CAN DATA ：第{num}个字节为： {hex_num} \n')
    elif choose_card == '2':
        s = ''.join(byte_example)
        hex_value = hex(int(s, 2))
        mfiu_crc_list.append(hex_value)
        print(f'CAN DATA ：第{num}个字节为： {hex_value}')


def Lfiu_byte(*channels):
    for i in range(10):
        byte_example = ['0'] * 8
        if i == 0:
            byte_example[1:4] = channels[0][::-1]
            byte_example[4:7] = channels[1][::-1]
            byte_example[7] = channels[2][::-1][0]
        elif i == 1:
            byte_example[1:3] = channels[2][::-1][1:3]
            byte_example[3:6] = channels[3][::-1]
            byte_example[6:8] = channels[4][::-1][0:2]
        elif i == 2:
            byte_example[1] = channels[4][::-1][2]
            byte_example[2:5] = channels[5][::-1]
            byte_example[5:8] = channels[6][::-1]
        elif i == 3:
            byte_example[1:4] = channels[7][::-1]
            byte_example[4:7] = channels[8][::-1]
            byte_example[7] = channels[9][::-1][0]
        elif i == 4:
            byte_example[1:3] = channels[9][::-1][1:3]
            byte_example[3:6] = channels[10][::-1]
            byte_example[6:8] = channels[11][::-1][0:2]
        elif i == 5:
            byte_example[1] = channels[11][::-1][2]
            byte_example[2:5] = channels[12][::-1]
            byte_example[5:8] = channels[13][::-1]
        # 101
        elif i == 6:
            byte_example[1:4] = channels[14][::-1]
            byte_example[4:7] = channels[15][::-1]
            byte_example[7] = channels[16][::-1][0]
        elif i == 7:
            byte_example[1:3] = channels[16][::-1][1:3]
            byte_example[3:6] = channels[17][::-1]
            byte_example[6:8] = channels[18][::-1][:2]
        elif i == 8:
            byte_example[0] = channels[23][::-1][0]
            byte_example[1] = channels[18][::-1][2]
            byte_example[2:5] = channels[19][::-1]
            byte_example[5:8] = channels[20][::-1]
        elif i == 9:
            byte_example[0] = channels[23][::-1][1]
            byte_example[1:4] = channels[21][::-1]
            byte_example[4:7] = channels[22][::-1]
            byte_example[7] = channels[23][::-1][2]
        result_bytes(i + 1, byte_example)


def Mfiu_bytes(*channels):
    for i in range(7):
        byte_example = ['0'] * 8

        if i == 1:
            byte_example[:3] = channels[0]
            byte_example[3:6] = channels[1]
            byte_example[6:8] = channels[2][:2]
        elif i == 2:
            byte_example[0] = channels[2][2]
            byte_example[1:4] = channels[3]
            byte_example[4:7] = channels[4]
            byte_example[7] = channels[5][0]
        elif i == 3:
            byte_example[:2] = channels[5][1:]
            byte_example[2:5] = channels[6]
            byte_example[5:8] = channels[7]
        # print(i+1,byte_example)
        result_bytes(i + 1, byte_example, '2')


def Hfiu_bytes(*channels):
    for i in range(7):
        byte_example = ['0'] * 8
        if i == 0:
            byte_example[0:3] = channels[0][::-1]
            byte_example[3:6] = channels[1][::-1]
            byte_example[6:8] = channels[2][::-1][:2]
        elif i == 1:
            byte_example[0] = channels[2][::-1][2]
            byte_example[1:4] = channels[3][::-1]
        result_bytes(i + 1, byte_example)


def strchannle2list(output_str):
    input_list = output_str.split()
    output_list = []
    for item in input_list:
        if '-' in item:
            output_list.append(item)
        else:
            output_list.append(str(item))
    input_list = []
    for i in output_list:
        if '-' not in i:
            input_list.append(i)
        else:
            range_start, range_end = i.split("-")
            input_list += range(int(range_start), int(range_end) + 1)
    input_list = [str(i) for i in input_list]
    return input_list


def strsign2list(output_str):
    input_list = output_str.split()
    output_list = []
    for item in input_list:
        if '*' in item:
            num, times = item.split('*')
            output_list += [num] * int(times)
        else:
            output_list.append(item)
    return output_list


def input_data(tmplist):
    print("example : 1 2 3 or 1-24 or 1 2 3 4-24")
    channle_a = input('请输入通道 ：')
    print("example : 1 1 1 1 1 or 1*5 or 1 1 1*3")
    sing_b = input('请输入通道状态 ：')
    channle_input = strchannle2list(channle_a)
    sign_input = strsign2list(sing_b)
    try:
        if len(sign_input) != len(channle_input):
            print('通道数量不一致，请重新输入')
            input_data([default_channle] * 24)
    except ValueError:
        print('输入错误')
    # 从列表中的每个元素中删除任何前导或尾随空格
    channle_input = [x.strip() for x in channle_input if x.strip()]
    # 从列表中删除任何重复的元素，同时保持剩余元素的顺序
    channle_input = list(OrderedDict.fromkeys(channle_input))
    for i, j in zip(channle_input, sign_input):
        for k, v in sign.items():
            if j == k:
                tmplist[int(i) - 1] = v
    print(tmplist, '###########')
    return tmplist


def auto_input_data(tmplist, channle_a, sing_b):
    # print("example : 1 2 3 or 1-24 or 1 2 3 4-24")
    # channle_a = input('请输入通道 ：')
    # print("example : 1 1 1 1 1 or 1*5 or 1 1 1*3")
    # sing_b = input('请输入通道状态 ：')
    channle_input = strchannle2list(channle_a)
    sign_input = strsign2list(sing_b)
    try:
        if len(sign_input) != len(channle_input):
            print('通道数量不一致，请重新输入')
            input_data([default_channle] * 24)
    except ValueError:
        print('输入错误')
    channle_input = [x.strip() for x in channle_input if x.strip()]
    channle_input = list(OrderedDict.fromkeys(channle_input))
    for i, j in zip(channle_input, sign_input):
        for k, v in sign.items():
            if j == k:
                tmplist[int(i) - 1] = v
    return tmplist


def Relay_sign_data():
    channles = [0] * 48
    print("example : 1 2 3 or 1-24 or 1 2 3 4-24")
    Relay_channle = input('请输入通道 ：')
    a = strchannle2list(Relay_channle)
    c_sublists = [channles[i:i + 8] for i in range(0, len(channles), 8)]
    ranges = {1: 0, 8: 0, 15: 1, 22: 2, 29: 3, 36: 4, 43: 5}
    for val in a:
        val = int(val)
        for range_end, sublist_index in ranges.items():
            if val < range_end:
                c_sublists[sublist_index][val - range_end + 8] = 1
                break
    num = 0
    for sublist in c_sublists:
        num += 1
        hex_value = hex(int(''.join(map(str, sublist)), 2))
        print(f'CAN DATA ：第{num}个字节为： {hex_value}')


def Relay_rate_data():
    print("example : 500,1000,125,250")
    Relay_rate = input('请输入波特率 ：')
    data1 = {'500': "02 F4 01 00 00 00 00 41",
             '125': "02 7D 00 00 00 00 00 43",
             '250': "02 FA 00 00 00 00 00 C1",
             '1000': "02 E8 03 00 00 00 00 6C"}
    print(data1.get(Relay_rate))


def Relay_ddsz():
    channles = [0] * 48
    print("example : 1 2 3 or 1-20 or 1 2 3 4-20")
    Relay_channle = input('请输入通道 ：')
    tmp = strchannle2list(Relay_channle)
    for val in tmp:
        if int(val) < 8:
            channles[int(val) - 1] = 1
        elif 15 > int(val) >= 8:
            channles[int(val)] = 1
        elif int(val) >= 15:
            channles[int(val) + 1] = 1
    c_sublists = [channles[i:i + 8] for i in range(0, len(channles), 8)]
    num = 0
    print(f'CAN ID : 210\n'
          "CAN DATA ：第1个字节为： 0x1")
    for sublist in c_sublists:
        num += 1
        hex_value = hex(int(''.join(map(str, sublist[::-1])), 2))
        print(f'CAN DATA ：第{num + 1}个字节为： {hex_value}')
    # 优化代码


def kype1200():
    t = input('t1 or tx or t1tx:\n')
    if t == 't1':
        a = input('通道2：T1主从模式:\n')
        b = input('通道1：T1主从模式:\n')
        c = input('通道2：T1速率自协商:\n')
        d = input('通道1：T1速率自协商:\n')
        e = input('通道2：T1速率:\n')
        f = input('通道1：T1速率:\n')
        ky1200_data = f'{a}{b}{c}{d}{e}{f}'
        hex_value = hex(int(ky1200_data, 2))
        hex_num = int(hex_value, 16)
        one_add_num = 0x05
        two_add_num = 0x03
        eight_byte = hex_num + one_add_num + two_add_num
        print(f'CAN ID : 0x7F0 \n'
              f'CAN DATA : 第1个字节为： 0x05\n'
              f'CAN DATA : 第2个字节为： 0x03\n'
              f'CAN DATA : 第3个字节为： {hex_value}\n'
              f'CAN DATA : 第4个字节为： 0x0\n'
              f'CAN DATA : 第5个字节为： 0x0\n'
              f'CAN DATA : 第6个字节为： 0x0\n'
              f'CAN DATA : 第7个字节为： 0x0\n'
              f'CAN DATA : 第8个字节为： {hex(eight_byte)}\n')

    elif t == 'tx':
        a = input('通道2：Tx工作模式:\n')
        b = input('通道1：Tx工作模式:\n')
        c = input('通道2：Tx速率自协商:\n')
        d = input('通道1：Tx速率自协商:\n')
        e = input('通道2：Tx速率:\n')
        f = input('通道1：Tx速率:\n')
        ky1200_data = f'{a}{b}{c}{d}{e}{f}'
        hex_value = hex(int(ky1200_data, 2))
        hex_num = int(hex_value, 16)
        one_add_num = 0x05
        two_add_num = 0x03
        eight_byte = hex_num + one_add_num + two_add_num
        print(f'CAN ID : 0x7F0 \n'
              f'CAN DATA : 第1个字节为： 0x05\n'
              f'CAN DATA : 第2个字节为： 0x03\n'
              f'CAN DATA : 第3个字节为： 0x0\n'
              f'CAN DATA : 第4个字节为： {hex_value}\n'
              f'CAN DATA : 第5个字节为： 0x0\n'
              f'CAN DATA : 第6个字节为： 0x0\n'
              f'CAN DATA : 第7个字节为： 0x0\n'
              f'CAN DATA : 第8个字节为： {hex(eight_byte)}\n')
    else:
        ta = input('通道2：T1主从模式:\n')
        tb = input('通道1：T1主从模式:\n')
        tc = input('通道2：T1速率自协商:\n')
        td = input('通道1：T1速率自协商:\n')
        te = input('通道2：T1速率:\n')
        tf = input('通道1：T1速率:\n')
        ky1200_data = f'{ta}{tb}{tc}{td}{te}{tf}'
        thex_value = hex(int(ky1200_data, 2))
        thex_num = int(thex_value, 16)
        a = input('通道2：Tx工作模式:\n')
        b = input('通道1：Tx工作模式:\n')
        c = input('通道2：Tx速率自协商:\n')
        d = input('通道1：Tx速率自协商:\n')
        e = input('通道2：Tx速率:\n')
        f = input('通道1：Tx速率:\n')
        ky1200_data = f'{a}{b}{c}{d}{e}{f}'
        hex_value = hex(int(ky1200_data, 2))
        hex_num = int(hex_value, 16)
        one_add_num = 0x05
        two_add_num = 0x03
        eight_byte = hex_num + one_add_num + two_add_num + thex_num
        print(f'CAN ID : 0x7F0 \n'
              f'CAN DATA : 第1个字节为： 0x05\n'
              f'CAN DATA : 第2个字节为： 0x03\n'
              f'CAN DATA : 第3个字节为： {thex_value}\n'
              f'CAN DATA : 第4个字节为： {hex_value}\n'
              f'CAN DATA : 第5个字节为： 0x0\n'
              f'CAN DATA : 第6个字节为： 0x0\n'
              f'CAN DATA : 第7个字节为： 0x0\n'
              f'CAN DATA : 第8个字节为： {hex(eight_byte)}\n')


def dianxinfuzai():
    print('测试电压或电流')
    t = input('V or A :')
    candata = [['0'] * 8 for _ in range(8)]
    if t == 'V' or 'v':
        print("example : 1 2 3 or 1-24 or 1 2 3 4-24")
        channle_a = input('请输入通道 :\n')
        channle_mv = input('请输入电压(mV) :\n')
        channels_list = strchannle2list(channle_a)
        ch_mv = channle_mv.split()
        # 检查用户输入的通道
        valid_channels = {'1', '2', '3', '4', '5', '6'}
        channels = set(channels_list)
        canid = ''
        if channels.issubset(valid_channels) and len(channels) > 0:
            if channels.issubset({'1', '2', '3'}):
                canid = '0x646'
                for i, j in zip(channels_list, ch_mv):
                    decimal_number = int(j)
                    hexadecimal_string1 = '{:02X}'.format((decimal_number >> 8) & 0xFF)
                    hexadecimal_string2 = '{:02X}'.format(decimal_number & 0xFF)
                    candata[0][int(i)-1] = '1'
                    if i == '1':
                        candata[int(i)] = str(hexadecimal_string1)
                        candata[int(i)+1] = str(hexadecimal_string2)
                    elif i == '2':
                        candata[int(i)+1] = str(hexadecimal_string1)
                        candata[int(i) + 2] = str(hexadecimal_string2)
                    elif i == '3':
                        candata[int(i)+2] = str(hexadecimal_string1)
                        candata[int(i) + 3] = str(hexadecimal_string2)

            elif channels.issubset({'4', '5', '6'}):
                canid = '0x647'
                for i, j in zip(channels_list, ch_mv):
                    decimal_number = int(j)
                    hexadecimal_string1 = '{:02X}'.format((decimal_number >> 8) & 0xFF)
                    hexadecimal_string2 = '{:02X}'.format(decimal_number & 0xFF)
                    candata[0][int(i)-4] = '1'
                    if i == '4':
                        candata[int(i)-3] = str(hexadecimal_string1)
                        candata[int(i)+1-3] = str(hexadecimal_string2)
                    elif i == '5':
                        candata[int(i)+1-3] = str(hexadecimal_string1)
                        candata[int(i) + 2-3] = str(hexadecimal_string2)
                    elif i == '6':
                        candata[int(i)+2-3] = str(hexadecimal_string1)
                        candata[int(i) + 3-3] = str(hexadecimal_string2)
            else:
                print("无效的通道组合或通道未在允许的范围内")  # 不支持的组合
        else:
            print("无效的通道组合或通道未在允许的范围内")
        # 修改candata中的元素为十六进制字符串
        for i in range(len(candata)):
            if isinstance(candata[i], list):
                binary_str = ''.join(candata[i])
                # 使用 int() 函数将二进制字符串转换为整数
                decimal_number = int(binary_str[::-1], 2)
                # 使用 hex() 函数将整数转换为十六进制字符串
                hexadecimal_string = hex(decimal_number)
                candata[i] = hexadecimal_string[2:]
        print(f'CAN ID: {canid}   \n'
              f'CAN DATA: {candata} \n')
    if t == 'A' or 'a':
        print("example : 1 2 3 or 1-24 or 1 2 3 4-24")
        channle_a = input('请输入通道 :\n')
        channle_mA = input('请输入电流(mA) :\n')
        channels_list = strchannle2list(channle_a)
        ch_mA = channle_mA.split()
        # 检查用户输入的通道
        valid_channels = {'1', '2', '3', '4', '5', '6'}
        channels = set(channels_list)
        canid = ''
        if channels.issubset(valid_channels) and len(channels) > 0:
            if channels.issubset({'1', '2', '3'}):
                canid = '0x644'
                for i, j in zip(channels_list, ch_mA):
                    decimal_number = int(j)
                    hexadecimal_string1 = '{:02X}'.format((decimal_number >> 8) & 0xFF)
                    hexadecimal_string2 = '{:02X}'.format(decimal_number & 0xFF)
                    if i == '1':
                        candata[int(i)-1] = str(hexadecimal_string1)
                        candata[int(i)] = str(hexadecimal_string2)
                    elif i == '2':
                        candata[int(i)] = str(hexadecimal_string1)
                        candata[int(i) + 1] = str(hexadecimal_string2)
                    elif i == '3':
                        candata[int(i)+1] = str(hexadecimal_string1)
                        candata[int(i) + 2] = str(hexadecimal_string2)
            elif channels.issubset({'4', '5', '6'}):
                canid = '0x645'
                for i, j in zip(channels_list, ch_mA):
                    decimal_number = int(j)
                    hexadecimal_string1 = '{:02X}'.format((decimal_number >> 8) & 0xFF)
                    hexadecimal_string2 = '{:02X}'.format(decimal_number & 0xFF)
                    if i == '4':
                        candata[int(i)-4] = str(hexadecimal_string1)
                        candata[int(i)-3] = str(hexadecimal_string2)
                    elif i == '5':
                        candata[int(i)-3] = str(hexadecimal_string1)
                        candata[int(i)-2] = str(hexadecimal_string2)
                    elif i == '6':
                        candata[int(i)-2] = str(hexadecimal_string1)
                        candata[int(i)-1] = str(hexadecimal_string2)
            else:
                print("无效的通道组合或通道未在允许的范围内")  # 不支持的组合
        else:
            print("无效的通道组合或通道未在允许的范围内")
        for i in range(len(candata)):
            if isinstance(candata[i], list):
                binary_str = ''.join(candata[i])
                # 使用 int() 函数将二进制字符串转换为整数
                decimal_number = int(binary_str[::-1], 2)
                # 使用 hex() 函数将整数转换为十六进制字符串
                hexadecimal_string = hex(decimal_number)
                candata[i] = hexadecimal_string[2:]
        print(f'CAN ID: {canid}   \n'
              f'CAN DATA: {candata} \n')
def main():
    choose_card = input("1: LFIU\n"
                        "2: MFIU \n"
                        "3: HFIU \n"
                        "4: Relay控制信号 \n"
                        "5: Relay波特率 \n"
                        "6: Relay单刀双掷  \n"
                        "7: kype1200   \n"
                        "8: 电芯负载   \n"
                        "请输入对应板卡型号的编号:")
    while True:
        if choose_card == '2':
            mfiu_crc_list.clear()
            temp_Mfiu = input_data([default_channle] * 8)
            Mfiu_bytes(*temp_Mfiu)
            int_list = [f'{int(x, 16):02x}' for x in mfiu_crc_list]
            results = ' '.join(int_list)
            crc_ver(results)
        elif choose_card == '1':
            temps_Lfiu = input_data([default_channle] * 24)
            Lfiu_byte(*temps_Lfiu)
        elif choose_card == '3':
            temp_Hfiu = input_data([default_channle] * 4)
            Hfiu_bytes(*temp_Hfiu)
        elif choose_card == '4':
            Relay_sign_data()
        elif choose_card == '5':
            Relay_rate_data()
        elif choose_card == '6':
            Relay_ddsz()
        elif choose_card == '7':
            kype1200()
        elif choose_card == '8':
            dianxinfuzai()


main()

