import os
import sys
from flask import Flask, render_template, request, jsonify, send_file, redirect
import paramiko
import threading
from route.tek import tektronix_bp
from route.fluke import fluke_bp
from route.dianchifuzai import dianchifuzai_bp
from route.oscilloscope import oscilloscope_bp
from route.itech import itech_bp
from route.vcardas import vcardas_bp
from route.ethercat import ethercat_bp
import pandas as pd
from utils.testcase.testcase import *

# if getattr(sys, 'frozen', False):
#     template_folder = os.path.join(sys._MEIPASS, 'templates')
#     static_folder = os.path.join(sys._MEIPASS, 'static')
#     app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
# else:
app = Flask(__name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')

app.register_blueprint(tektronix_bp, url_prefix='/tek')
app.register_blueprint(fluke_bp, url_prefix='/fluke')
app.register_blueprint(dianchifuzai_bp, url_prefix='/dianchifuzai')
app.register_blueprint(oscilloscope_bp, url_prefix='/oscilloscope')
app.register_blueprint(itech_bp, url_prefix='/itech')
app.register_blueprint(vcardas_bp, url_prefix='/vcardas')
app.register_blueprint(ethercat_bp, url_prefix='/ethercat')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/oscilloscope')
def oscilloscope():
    return render_template('oscilloscope.html')


@app.route('/itech')
def itech():
    return render_template('itech.html')


@app.route('/vcardas')
def vcardas():
    return render_template('vcardas.html')


@app.route('/fluke')
def fluke():
    return render_template('fluke.html')


@app.route('/tek')
def tek():
    return render_template('tek.html')


@app.route('/dianchifuzai')
def dianchifuzai():
    return render_template('dianchifuzai.html')


@app.route('/ethercat')
def ethercat():
    return render_template('ethercat.html')


# @app.route('/testcase')
# def testcase():
#     uploaded_files = os.listdir('uploads')
#     return render_template('testcase.html', uploaded_files=uploaded_files)
#     # return render_template('testcase.html')


@app.route('/testcase')
def testcase():
    uploaded_files = os.listdir(f'uploads')
    return render_template('create_project.html',
                           uploaded_files=uploaded_files)
    # return render_template('testcase.html')


# SSH连接配置
ssh_host = '192.168.10.207'
ssh_port = 22
ssh_username = 'rtpc'
ssh_password = 'sv123'
ssh_client = None  # 保持SSH连接全局变量
ssh_lock = threading.Lock()


def close_ssh_connection():
    global ssh_client
    if ssh_client is not None:
        with ssh_lock:
            ssh_client.close()
            ssh_client = None


@app.route('/download_visa', methods=['GET'])
def download_visa():
    # 获取要下载的文件名
    file_name = 'ni-visa_23.5.0_offline.iso'

    try:
        # 初始化SSH客户端，如果连接不存在则创建连接
        global ssh_client
        if ssh_client is None:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ssh_host, ssh_port, ssh_username, ssh_password)

            # 创建一个定时器线程，在20分钟后自动关闭连接
            timer = threading.Timer(3600, close_ssh_connection)
            timer.start()

        # 下载文件
        sftp = ssh_client.open_sftp()
        remote_path = f'/home/rtpc/{file_name}'  # 远程文件路径

        # 直接发送文件作为响应，而不保存到本地
        return sftp_file_as_response(sftp, remote_path, file_name)
    except Exception as e:
        return f"下载文件失败: {str(e)}"


def sftp_file_as_response(sftp, remote_path, file_name):
    file_handle = sftp.file(remote_path)
    # 发送文件作为响应
    response = send_file(file_handle,
                         as_attachment=True,
                         download_name=file_name)
    return response


@app.route('/download_pdf')
def download_pdf():
    pdf_file_path = 'static/ProgrammingGuide_EN11D.pdf'
    download_name = 'ProgrammingGuide_EN11D.pdf'

    # Check if the PDF file exists
    if os.path.exists(pdf_file_path):
        # Send the file to the client for download
        return send_file(pdf_file_path,
                         as_attachment=True,
                         download_name=download_name)
    else:
        return "PDF file not found"


@app.route('/download_pdf_it')
def download_pdf_it():
    pdf_file_path = 'static/IT6700_Programming_Guide-CN.pdf'
    download_name = 'IT6700_Programming_Guide-CN.pdf'

    # Check if the PDF file exists
    if os.path.exists(pdf_file_path):
        # Send the file to the client for download
        return send_file(pdf_file_path,
                         as_attachment=True,
                         download_name=download_name)
    else:
        return "PDF file not found"


@app.route('/download_pdf_signal')
def download_pdf_signal():
    pdf_file_path = 'static/AFG1000-Programmer-Manual-EN-077112901(20160719)-RevA.pdf'
    download_name = 'AFG1000-Programmer-Manual-EN-077112901(20160719)-RevA.pdf'

    # Check if the PDF file exists
    if os.path.exists(pdf_file_path):
        # Send the file to the client for download
        return send_file(pdf_file_path,
                         as_attachment=True,
                         download_name=download_name)
    else:
        return "PDF file not found"


@app.route('/download_pdf_fluke')
def download_pdf_fluke():
    pdf_file_path = 'static/fluke_8808a_multimeter_manual.pdf'
    download_name = 'fluke_8808a_multimeter_manual.pdf'

    # Check if the PDF file exists
    if os.path.exists(pdf_file_path):
        # Send the file to the client for download
        return send_file(pdf_file_path,
                         as_attachment=True,
                         download_name=download_name)
    else:
        return "PDF file not found"


@app.route('/download_pdf_vcardas')
def download_pdf_vcardas():
    pdf_file_path = 'static/VCarDAS-Introductions.chm'
    download_name = 'VCarDAS-Introductions.chm'

    # Check if the PDF file exists
    if os.path.exists(pdf_file_path):
        # Send the file to the client for download
        return send_file(pdf_file_path,
                         as_attachment=True,
                         download_name=download_name)
    else:
        return "PDF file not found"


@app.route('/download_exe_calculator', methods=['GET'])
def download_exe_calculator():
    pdf_file_path = 'static/can_data_calculator.exe'
    download_name = 'can_data_calculator.exe'

    # Check if the PDF file exists
    if os.path.exists(pdf_file_path):
        # Send the file to the client for download
        return send_file(pdf_file_path,
                         as_attachment=True,
                         download_name=download_name)
    else:
        return "exe  not found"


# 项目接口

# 设置文件上传的目录
app.config['UPLOAD_FOLDER'] = 'uploads'

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'csv'}


@app.route('/create_project', methods=['POST'])
def create_project():
    project_name = request.form.get('project_name')
    if project_name:
        # 调用后端接口完成创建（这里只是示例，您需要根据您的需求实现该接口）
        # 创建成功后保存项目名称
        project_folder = os.path.join('uploads', project_name)
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
        return jsonify({'message': '项目创建成功'})
    else:
        return jsonify({'message': '项目名称不能为空'})


@app.route('/project/<project_name>')
def project_page(project_name):
    uploaded_files = os.listdir(f'uploads/{project_name}')
    return render_template('testcase.html',
                           uploaded_files=uploaded_files,
                           project_name=project_name)


@app.route('/get_project_list')
def get_project_list():
    project_list = [
        folder for folder in os.listdir('uploads')
        if os.path.isdir(os.path.join('uploads', folder))
    ]
    return jsonify({'projects': project_list})


@app.route('/search_projects')
def search_projects():
    query = request.args.get('query')
    if not query:
        return jsonify({'projects': []})
    project_list = [
        folder for folder in os.listdir('uploads')
        if os.path.isdir(os.path.join('uploads', folder)) and query in folder
    ]
    return jsonify({'projects': project_list})


# 辅助函数：检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/testcase/upload', methods=['POST'])
def test_case_upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    project_name = request.form['project']

    if file.filename == '':
        return "请选择文件"

    # if project_name and file:
    #     if allowed_file(file.filename):
    #         project_folder = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
    #         if not os.path.exists(project_folder):
    #             os.makedirs(project_folder)
    #
    #         file.save(os.path.join(project_folder, file.filename))

    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        project_folder = os.path.join(app.config['UPLOAD_FOLDER'],
                                      project_name)
        file.save(os.path.join(project_folder, file.filename))
        return redirect(f'/project/{project_name}')
    else:
        return "只支持上传csv文件"


@app.route('/testcase/delete_file', methods=['DELETE'])
def delete_file():
    filename = request.args.get('filename')
    project_name = request.args.get('project')
    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        project_folder = os.path.join(app.config['UPLOAD_FOLDER'],
                                      project_name)
        pro_file_del = os.path.join(project_folder, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            os.remove(pro_file_del)
            return redirect(f'/project/{project_name}')
        else:
            return jsonify({'error': '文件不存在'}, 404)
    else:
        return jsonify({'error': '未提供文件名'}, 400)


@app.route('/testcase/view/<filename>')
def view_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # 读取CSV文件并将其转换为HTML表格
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path, encoding='gb2312')
        data.fillna("Na", inplace=True)
        table_html = data.to_html(classes='table table-bordered', index=False)

        return render_template('view_csv.html', table=table_html)

    return "File format not supported."


@app.route('/testcase/download_file')
def download_file():
    filename = request.args.get('filename')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)


@app.route('/testcase/run_csvload', methods=['GET'])
def run_csvload():
    try:
        filename = request.args.get('filename')
        csvload(BASE_URL='http://127.0.0.1:8000',
                csv_file=f"./uploads/{filename}")
        return jsonify({"message": "自动化测试用例运行完成"})
    except Exception as e:
        return jsonify({"error": str(e)})


project_names = []


@app.route('/testcase/create_project', methods=['POST'])
def run_create_project():
    project_name = request.form.get('project_name')
    if project_name:
        project_names.append(project_name)

        # Save the project names to a text file (you can use a database in a real application)
        with open('project_names.txt', 'a') as file:
            file.write(project_name + '\n')

        return jsonify({'message': 'Project created successfully'})
    else:
        return jsonify({'message': 'Project name cannot be empty'}, 400)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # 使服务器外部可见
        port=8000,  # 改变默认端口为8000
        debug=True)
