from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
import os
from utils.ocr_processing import extract_text_from_image
from utils.gemini_integration import analyze_text_with_gemini, analyze_text_with_image, analyze_audio_with_gemini
from werkzeug.utils import secure_filename
from io import BytesIO
from elevenlabs.client import ElevenLabs
from elevenlabs import stream

app = Flask(__name__)

# Cấu hình cơ sở dữ liệu
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://fmu76a694pv7tx5b:igvaouje2t8tcxgd@yhrz9vns005e0734.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/q8b1v3rybj8kvaiu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Needed if you plan to use flash messages

# Initialize ElevenLabs client
client = ElevenLabs(api_key="sk_89c7d9a5cc4ac949a91b7bfc92c47be8115ae6e2a4f4b17a")

analysis_result = ""

# Cấu hình thư mục tải lên
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','webp'}
app.config['UPLOAD_FOLDER'] = 'uploads'  # Đặt tên cho thư mục tải lên

# Kiểm tra đuôi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# Định nghĩa mô hình User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Tạo cơ sở dữ liệu nếu chưa tồn tại
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()  # Kiểm tra thông tin đăng nhập
        
        if user:
            session['username'] = user.username  # Lưu tên người dùng vào session
            #flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Xóa tên người dùng khỏi session
    #flash("Logged out successfully!", "success")
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Kiểm tra xem người dùng đã tồn tại chưa
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or Email already exists", "danger")
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully!", "success")
            return redirect(url_for('login'))
    
    return render_template('signup.html')

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

@app.route('/health_analysis', methods=['GET', 'POST'])
def health_analysis():
    if request.method == 'POST':
        # Kiểm tra xem file đã được tải lên chưa
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        
        # Nếu không có file được chọn, báo cho người dùng
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Lưu file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Phân tích tin nhắn và ảnh
            text_prompt = "Hãy phân tích tình trạng thể chất của người trong bức ảnh này. Xin hãy đánh giá các yếu tố như thể trạng tổng thể, chỉ số cơ thể có thể suy đoán (như vóc dáng, sức mạnh cơ bắp, mức độ linh hoạt), khả năng hoạt động thể chất, và tiềm năng thực hiện các loại hình thể dục khác nhau. Nếu có thể, hãy đưa ra những nhận xét tinh tế và động viên để giúp người này nhận thức rõ hơn về sức khỏe của mình, cùng một số lời khuyên hữu ích để phát triển lối sống lành mạnh."
            result = analyze_text_with_image(text_prompt, file_path)

            # Hiện kết quae
            return render_template('health_analysis.html', health_analysis_result=result)

    return render_template('health_analysis.html')

@app.route('/ai_doctor')
def ai_doctor():
    return render_template('ai_doctor.html')

def stream_text_to_speech(text):
    # Stream text-to-speech response directly from ElevenLabs
    audio_stream = client.generate(
        text=text,
        voice="Eric",  # Choose the desired voice
        model="eleven_turbo_v2_5",
        stream=True
    )
    return audio_stream

@app.route('/analyze_audio', methods=['POST'])
def analyze_audio():
    global analysis_result  # Use a global variable to store the analysis result

    # Check if audio is in request files
    if 'audio' not in request.files:
        return jsonify({"result": "Lỗi: Không tìm thấy tệp âm thanh."}), 400

    audio_file = request.files['audio']
    audio_file_path = f"/tmp/{audio_file.filename}"
    audio_file.save(audio_file_path)

    # Assuming analyze_audio_with_gemini is a function that processes the audio
    # and returns the analysis result as a string
    analysis_result = analyze_audio_with_gemini(audio_file_path)

    # If we have an analysis result, start streaming audio in response
    if analysis_result:
        return jsonify({"result": analysis_result, "audio_url": "/stream_audio"})
    else:
        return jsonify({"result": "Lỗi: Không thể tạo tệp âm thanh."}), 500

@app.route('/stream_audio')
def stream_audio():
    global analysis_result

    if analysis_result:
        audio_stream = stream_text_to_speech(analysis_result)

        def generate_audio():
            for chunk in audio_stream:
                if chunk:
                    yield chunk

            # Reset `analysis_result` after streaming completes
            global analysis_result
            analysis_result = None

        return Response(generate_audio(), mimetype="audio/wav")
    else:
        return jsonify({"result": "Lỗi: Không có kết quả phân tích."}), 400

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    # Bind to the Heroku-specified port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)