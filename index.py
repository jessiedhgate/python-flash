from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
import os
import random
import re

app = FastAPI()

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

def process_file(input_path, output_path, num_modules):
    # 省略长代码逻辑，保持原始功能不变
    pass  # 复制原始 `process_file` 函数的内容

@app.post("/process/")
async def process_file_api(file: UploadFile, num_modules: int = Form(1)):
    # 保存上传的文件
    input_path = f"/tmp/{file.filename}"
    with open(input_path, "wb") as f:
        f.write(await file.read())
    
    # 输出路径
    output_path = "/tmp/output.txt"
    process_file(input_path, output_path, num_modules)

    return FileResponse(output_path, filename="processed_output.txt")
