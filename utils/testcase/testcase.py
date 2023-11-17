# -*- coding: utf-8 -*-
import csv
import json
import requests
from time import sleep
import os
import subprocess

# BASE_URL = 'http://127.0.0.1:8000'
HEADERS = {'Content-Type': 'application/json'}
# HEADERS = {'Content-type': 'multipart/form-data'}


def read_test_cases_from_csv(csv_file):
    test_cases = []
    with open(csv_file, 'r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # 处理 'data' 字段中的 'command'，去除反斜杠
            command = row['data'].replace('\\', '')
            # 更新 'command' 字段
            row['data'] = command
            test_cases.append(row)
    return test_cases


def wirte_test_result_into_csv(csv_file, index, wd):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        # 修改指定单元格的值
        # 假设我们要修改第2行第3列（注意：索引是从0开始的）的值
        data[int(index)][10] = wd
        # 重新写入文件
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def csvload(BASE_URL, csv_file):
    # 测试用例数据
    test_cases = read_test_cases_from_csv(csv_file)

    # 创建一个列表来存储分组后的测试用例
    grouped_test_cases = []
    current_group = []

    for test_case in test_cases:
        test_case_number = test_case['编号']

        if test_case_number:
            # 如果当前测试用例具有编号，说明它是一个新的组的开始
            if current_group:
                # 如果当前组不为空，则将其添加到分组列表中
                grouped_test_cases.append(current_group)
            current_group = [test_case]  # 创建一个新的组并将当前测试用例添加到组中
        else:
            # 如果测试用例没有编号，说明它仍属于当前组，因此将其添加到当前组中
            current_group.append(test_case)

    # 确保添加最后一个组
    if current_group:
        # 确保最后一个组也添加到分组列表中
        grouped_test_cases.append(current_group)

    # 打印分组后的测试用例
    num = 0
    for group_index, group_test_cases in enumerate(grouped_test_cases,
                                                   start=1):
        # 遍历分组列表，每个group_test_cases代表一个组
        print(f"第{group_index}条用例需要执行{len(group_test_cases)}步操作:")
        for test_case in group_test_cases:
            # 列出csv值
            num += 1
            csv_name = test_case['测试用例名称']
            csv_qianzhitiaojian = test_case['前置条件']
            csv_ceshibuzou = test_case['测试步骤']
            csv_url = test_case['url']
            csv_method = test_case['method']
            csv_jsondata = test_case['data']
            csv_isrun = test_case['是否运行']
            csv_houzhitiaojian = test_case['后置条件']
            csv_result = test_case['返回结果']
            # print(csv_qianzhitiaojian.split())
            headers = HEADERS.copy()
            url = BASE_URL + csv_url
            jsondata = json.loads(
                csv_jsondata) if '{' in csv_jsondata else csv_jsondata
            if csv_isrun == '是':
                if csv_qianzhitiaojian.split():
                    for i in csv_qianzhitiaojian.split('\n'):
                        print(i)
                        eval(f"""{i}""")
                response = None
                try:
                    if csv_method == 'GET':
                        response = requests.get(url + str(jsondata),
                                                headers=headers)
                    elif csv_method == 'POST':
                        response = requests.post(url,
                                                 headers=headers,
                                                 json=jsondata)
                    # print(response.json(),response.text)
                    wirte_test_result_into_csv(csv_file, num, response.json())
                    # 可以根据其他HTTP方法扩展
                except Exception as e:
                    print(
                        f"Exception occurred during test execution: {str(e)}")
                    return None
                if csv_houzhitiaojian.split():
                    for i in csv_houzhitiaojian.split():
                        eval(f"""{i}""")
            else:
                pass
