# app.py
from flask import Flask, render_template, request, redirect, url_for
import os
from utils.ocr_processing import extract_text_from_image
from utils.gemini_integration import analyze_text_with_gemini

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Giới hạn tải lên tập tin là 16 MB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        # Ensure the 'uploads' folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Xử lý OCR
        raw_text = extract_text_from_image(filepath)
        
        # Phân tích với Gemini AI
        extracted_entities = analyze_text_with_gemini(raw_text).replace('\n', ' ')  # Đảm bảo hiển thị trên một dòng
        
        # Xóa tập tin sau khi xử lý
        os.remove(filepath)
        
        # Hiển thị kết quả
        return render_template('index.html', extracted_text=raw_text, extracted_entities=extracted_entities)
    return redirect(request.url)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    # Bind to the Heroku-specified port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
