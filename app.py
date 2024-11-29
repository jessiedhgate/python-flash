import os
import random
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_file(file_path, special_string):
    output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], "processed_" + os.path.basename(file_path))
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 找到所有特殊字符的行号
    special_line_indices = [index for index, line in enumerate(lines) if special_string in line]

    block_rows = []
    for i in range(len(special_line_indices) - 1):
        start_index = special_line_indices[i] + 1
        end_index = special_line_indices[i + 1]
        block_rows.append(lines[start_index:end_index])

    num_rows = len(block_rows[0]) if block_rows else 0
    if not all(len(block) == num_rows for block in block_rows):
        raise ValueError("所有特殊字符块下的行数不一致，无法处理。")

    randomized_blocks = []
    for block in block_rows:
        randomized_block = block[:]
        for row_index in range(num_rows):
            sixth_values = []
            for b in block_rows:
                line = b[row_index]
                columns = line.split()
                if len(columns) >= 6:
                    try:
                        sixth_values.append(float(columns[5]))
                    except ValueError:
                        continue

            if sixth_values:
                max_val = max(sixth_values)
                min_val = min(sixth_values)
                random_value = round(random.uniform(min_val, max_val), 3)
                original_line = randomized_block[row_index]
                columns = original_line.split()
                if len(columns) >= 6:
                    columns[5] = f"{random_value:.3f}"
                    randomized_block[row_index] = " ".join(columns) + "\n"
        randomized_blocks.append(randomized_block)

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for i, block in enumerate(randomized_blocks):
            output_file.write(lines[special_line_indices[i]])
            output_file.writelines(block)
        if special_line_indices:
            output_file.writelines(lines[special_line_indices[-1] + 1:])

    return output_file_path


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        special_string = request.form['special_string']
        if 'file' not in request.files:
            return "没有选择文件"
        file = request.files['file']
        if file.filename == '':
            return "没有选择文件"
        if file:
            filename = secure_filename(file.filename)
            input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_file_path)

            try:
                output_file_path = process_file(input_file_path, special_string)
                return redirect(url_for('download_file', filename=os.path.basename(output_file_path)))
            except Exception as e:
                return f"处理文件时出错: {e}"

    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

