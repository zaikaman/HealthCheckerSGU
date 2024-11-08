from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
import os
from utils.gemini_integration import analyze_text_with_image, analyze_audio_with_gemini
from werkzeug.utils import secure_filename
from elevenlabs.client import ElevenLabs
from datetime import datetime
from cloudinary import config, uploader

app = Flask(__name__)

# Cấu hình cơ sở dữ liệu
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://yh2k7r2tjiynygfo:chsl4bzvipbei6jc@o3iyl77734b9n3tg.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/wk5ybqcvorkax5bp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Khởi tạo ElevenLabs client
client = ElevenLabs(api_key="sk_0282f7067c9709491cbe2e584d4d993a0cb07b2a1fe0aa42")

analysis_result = ""

# Cấu hình thư mục tải lên
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = 'uploads'

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

# Thêm vào phần đầu file, sau class User
class FileAnalysis(db.Model):
    __tablename__ = 'tbl_file_analysis'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    input = db.Column(db.Text, nullable=False)  # Lưu tên file
    output = db.Column(db.Text, nullable=False)  # Lưu kết quả phân tích
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthAnalysis(db.Model):
    __tablename__ = 'tbl_health_analysis'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    input = db.Column(db.Text, nullable=False)  # Lưu tên file ảnh
    output = db.Column(db.Text, nullable=False)  # Lưu kết quả phân tích
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AiDoctor(db.Model):
    __tablename__ = 'tbl_ai_doctor'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    input = db.Column(db.Text, nullable=False)  # Lưu file audio
    output = db.Column(db.Text, nullable=False)  # Lưu kết quả phân tích
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tạo cơ sở dữ liệu nếu chưa tồn tại
with app.app_context():
    db.create_all()

# Cấu hình Cloudinary
config(
    cloud_name="ddrfu9ftt",
    api_key="419138417289347", 
    api_secret="419138417289347"
)

# Hàm upload file lên Cloudinary
def upload_to_cloudinary(file, folder):
    try:
        result = uploader.upload(
            file,
            folder=f"healthchecker/{folder}",
            resource_type="auto"
        )
        return result['secure_url']
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/file_analysis', methods=['GET', 'POST'])
def file_analysis():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
            
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                # Upload to Cloudinary
                result = uploader.upload(file, folder="healthchecker/medical")
                file_url = result['secure_url']
                
                # Analyze with Gemini
                text_prompt = "Analyze this medical record or prescription and extract key information in Vietnamese"
                extracted_entities = analyze_text_with_image(text_prompt, file)
                
                # Save to database
                if 'username' in session:
                    user = User.query.filter_by(username=session['username']).first()
                    analysis = FileAnalysis(
                        email=user.email,
                        input=file_url,
                        output=extracted_entities
                    )
                    db.session.add(analysis)
                    db.session.commit()
                
                return render_template('file_analysis.html', extracted_entities=extracted_entities)
                
            except Exception as e:
                print(f"Error: {str(e)}")
                return redirect(request.url)
                
    return render_template('file_analysis.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
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

@app.route('/health_analysis', methods=['GET', 'POST'])
def health_analysis():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
            
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                # Upload to Cloudinary
                result = uploader.upload(file, folder="healthchecker/health")
                file_url = result['secure_url']
                
                # Analyze with Gemini
                text_prompt = "Analyze this person's physical condition and health status in Vietnamese"
                analysis_result = analyze_text_with_image(text_prompt, file)
                
                # Save to database
                if 'username' in session:
                    user = User.query.filter_by(username=session['username']).first()
                    analysis = HealthAnalysis(
                        email=user.email,
                        input=file_url,
                        output=analysis_result
                    )
                    db.session.add(analysis)
                    db.session.commit()
                
                return render_template('health_analysis.html', health_analysis_result=analysis_result)
                
            except Exception as e:
                print(f"Error: {str(e)}")
                return redirect(request.url)
                
    return render_template('health_analysis.html')

@app.route('/ai_doctor')
def ai_doctor():
    return render_template('ai_doctor.html')

def stream_text_to_speech(text):
    audio_stream = client.generate(
        text=text,
        voice="Eric",
        model="eleven_turbo_v2_5",
        stream=True
    )
    return audio_stream

@app.route('/analyze_audio', methods=['POST'])
def analyze_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
        
    audio_file = request.files['audio']
    
    try:
        # Upload to Cloudinary
        result = uploader.upload(
            audio_file,
            folder="healthchecker/audio",
            resource_type="video"  # For audio files
        )
        audio_url = result['secure_url']
        
        # Analyze with Gemini
        analysis_result = analyze_audio_with_gemini(audio_file)
        
        # Save to database
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            analysis = AiDoctor(
                email=user.email,
                input=audio_url,
                output=analysis_result
            )
            db.session.add(analysis)
            db.session.commit()
        
        return jsonify({
            "result": analysis_result,
            "audio_url": audio_url
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Upload or analysis failed"}), 500

@app.route('/stream_audio')
def stream_audio():
    analysis_result = request.args.get('result')
    
    if analysis_result:
        audio_stream = stream_text_to_speech(analysis_result)

        def generate_audio():
            for chunk in audio_stream:
                if chunk:
                    yield chunk

        return Response(generate_audio(), mimetype="audio/mpeg")
    else:
        return jsonify({"result": "Lỗi: Không có kết quả phân tích."}), 400

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    # Lấy lịch sử từ cả 3 bảng
    file_analyses = FileAnalysis.query.filter_by(email=user.email).order_by(FileAnalysis.created_at.desc()).all()
    health_analyses = HealthAnalysis.query.filter_by(email=user.email).order_by(HealthAnalysis.created_at.desc()).all()
    ai_doctor_analyses = AiDoctor.query.filter_by(email=user.email).order_by(AiDoctor.created_at.desc()).all()
    
    return render_template('history.html', 
                         file_analyses=file_analyses,
                         health_analyses=health_analyses,
                         ai_doctor_analyses=ai_doctor_analyses)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)