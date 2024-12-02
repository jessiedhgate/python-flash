import random
import re
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# 添加首页路由来渲染index.html
@app.route('/')
def index():
    return render_template('index.html')

def is_number(value):
    """检查一个值是否为数字（浮动或整数）。"""
    try:
        float(value)
        return True
    except ValueError:
        return False

def format_number(value, decimal_places):
    """格式化数值为指定小数位数的字符串，保留末尾的0。"""
    return f"{value:.{decimal_places}f}"

def process_file(input_file, num_modules):
    """根据提供的输入文件处理数据，并返回处理后的内容"""
    output_data = []
    row_generation_info = {}

    # 读取输入文件，保留行格式
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 识别大模块的行数
    big_modules = []
    current_module = []
    for line in lines:
        line = line.rstrip('\n')  # 去除行尾换行符
        if line.startswith("TCNT#"):
            if current_module:
                big_modules.append(current_module)  # 保存上一个大模块
            current_module = [line]  # 记录大模块的开始行
        else:
            current_module.append(line)

    # 最后一个大模块也需要保存
    if current_module:
        big_modules.append(current_module)

    # 截取或扩展模块数
    if len(big_modules) > num_modules:
        big_modules = big_modules[:num_modules]
    elif len(big_modules) < num_modules:
        while len(big_modules) < num_modules:
            new_module = []
            for original_line in big_modules[0]:
                new_module.append(original_line)
            big_modules.append(new_module)

    # 生成新的大模块数据
    for idx, module in enumerate(big_modules):
        new_module = []
        for line in module:
            columns = re.split(r"(\s+)", line)
            if line.startswith("TCNT#"):
                line = re.sub(r"(TCNT#)\s*\d*", f"\\1 {idx + 1}", line)
                new_module.append(line)
                continue
            if line.startswith("-"):
                new_module.append(line)
                continue
            new_line = ''.join(columns)
            new_module.append(new_line)

        output_data.extend(new_module)

    return output_data

@app.route('/process', methods=['POST'])
def process():
    """处理上传的文件，生成结果并返回"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    num_modules = int(request.form.get('num_modules', 1))

    # 保存上传的文件
    input_file = "/tmp/uploaded_file.txt"
    file.save(input_file)

    # 处理文件并返回结果
    output_data = process_file(input_file, num_modules)

    # 返回处理后的数据
    return jsonify({"processed_data": output_data})

if __name__ == '__main__':
    app.run(debug=True)
