from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from utils.gemini_integration import analyze_text_with_image, analyze_audio_with_gemini
from werkzeug.utils import secure_filename
from elevenlabs.client import ElevenLabs
from datetime import datetime, timedelta
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask_mail import Mail, Message
import jwt
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect
import logging

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
    verified = db.Column(db.Boolean, default=False)

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

def add_column_if_not_exists():
    try:
        # Lấy inspector từ engine của database
        inspector = inspect(db.engine)
        
        # Lấy danh sách các cột hiện có trong bảng user
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        # Kiểm tra nếu cột verified chưa tồn tại
        if 'verified' not in columns:
            # Tạo và thực thi câu lệnh ALTER TABLE
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE user ADD COLUMN verified BOOLEAN DEFAULT FALSE')
                conn.commit()
            print("Đã thêm cột 'verified' vào bảng user")
        else:
            print("Cột 'verified' đã tồn tại trong bảng user")
            
    except Exception as e:
        print(f"Lỗi khi kiểm tra/thêm cột: {str(e)}")

# Tạo cơ sở dữ liệu nếu chưa tồn tại
with app.app_context():
    db.create_all()
    add_column_if_not_exists()

# Thêm cấu hình Cloudinary (thay thế các giá trị bằng thông tin từ dashboard của bạn)
cloudinary.config(
    cloud_name = "ddrfu9ftt",
    api_key = "419138417289347",
    api_secret = "cm9Rws-Nh44hnuzHER4LBxK2gCY"
)

# Thêm cấu hình email sau app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'thinhgpt1706@gmail.com'  # Email của bạn
app.config['MAIL_PASSWORD'] = 'xgxn kjcv haqf sjxz'    # App password

# Khởi tạo Mail
mail = Mail(app)

# Thêm logging để debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_confirmation_token(email):
    return jwt.encode(
        {'email': email, 'exp': datetime.utcnow() + timedelta(hours=24)},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def send_confirmation_email(to_email, token):
    try:
        # Tạo URL xác nhận
        confirm_url = url_for('confirm_email', token=token, _external=True)
        
        # Tạo message
        msg = Message('Xác nhận tài khoản',
                     sender=app.config['MAIL_USERNAME'],
                     recipients=[to_email])
        
        # Nội dung email
        msg.body = f'''Để xác nhận tài khoản của bạn, vui lòng click vào link sau:
{confirm_url}

Link này sẽ hết hạn sau 24 giờ.
'''
        # Gửi email
        mail.send(msg)
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

# Hàm validate email
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/file_analysis', methods=['GET', 'POST'])
def file_analysis():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Không có file nào được chọn')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Không có file nào được chọn')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                # Lưu file vào uploads trước
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{secure_filename(file.filename.rsplit('.', 1)[0])}_{timestamp}.{file.filename.rsplit('.', 1)[1]}"
                filepath = os.path.join('uploads', filename)
                file.save(filepath)

                # Upload lên Cloudinary từ file local
                upload_result = cloudinary.uploader.upload(filepath,
                    public_id=f"file_analysis/{filename}",
                    folder="health_checker")
                file_url = upload_result['secure_url']

                # Phân tích với Gemini AI (sử dụng file local)
                text_prompt = "Hãy phân tích chi tiết hồ sơ y tế hoặc đơn thuốc này và đưa ra những thông tin quan trọng."
                extracted_entities = analyze_text_with_image(text_prompt, filepath)

                # Lưu vào database với Cloudinary URL
                user = User.query.filter_by(username=session['username']).first()
                analysis = FileAnalysis(
                    email=user.email,
                    input=file_url,
                    output=extracted_entities
                )
                db.session.add(analysis)
                db.session.commit()

                # Xóa file local sau khi đã upload xong
                os.remove(filepath)
                
                return render_template('file_analysis.html', extracted_entities=extracted_entities)

            except Exception as e:
                print(f"Error: {str(e)}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash('Có lỗi xảy ra khi xử lý file')
                return redirect(request.url)
    
    # Thêm return cho phương thức GET
    return render_template('file_analysis.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            if user.verified:
                session['username'] = user.username
                return redirect(url_for('index'))
            else:
                flash("Vui lòng xác nhận email trước khi đăng nhập", "warning")
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng", "danger")
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
        
        # Validate input
        if not username or not email or not password:
            flash("Vui lòng điền đầy đủ thông tin", "danger")
            return redirect(url_for('signup'))
            
        if not is_valid_email(email):
            flash("Email không hợp lệ", "danger")
            return redirect(url_for('signup'))
            
        if len(password) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự", "danger")
            return redirect(url_for('signup'))
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Tên đăng nhập hoặc Email đã tồn tại", "danger")
        else:
            # Hash password trước khi lưu
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username, 
                email=email, 
                password=hashed_password,
                verified=False
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                
                # Gửi email xác nhận
                token = generate_confirmation_token(email)
                if send_confirmation_email(email, token):
                    logger.info(f"Confirmation email sent to {email}")
                    flash("Tài khoản đã được tạo! Vui lòng kiểm tra email để xác nhận.", "success")
                else:
                    logger.error(f"Failed to send confirmation email to {email}")
                    flash("Có lỗi xảy ra khi gửi email xác nhận. Vui lòng thử lại.", "danger")
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error during signup: {str(e)}")
                flash("Có lỗi xảy ra, vui lòng thử lại sau", "danger")
    
    return render_template('signup.html')

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        email = decoded['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.verified = True
            db.session.commit()
            flash('Tài khoản của bạn đã được xác nhận! Bạn có thể đăng nhập ngay bây giờ.', 'success')
        else:
            flash('Link xác nhận không hợp lệ.', 'danger')
            
    except jwt.ExpiredSignatureError:
        flash('Link xác nhận đã hết hạn.', 'danger')
    except jwt.InvalidTokenError:
        flash('Link xác nhận không hợp lệ.', 'danger')
        
    return redirect(url_for('login'))

@app.route('/health_analysis', methods=['GET', 'POST'])
def health_analysis():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Không có file nào được chọn')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Không có file nào được chọn')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                # Lưu file vào uploads trước
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{secure_filename(file.filename.rsplit('.', 1)[0])}_{timestamp}.{file.filename.rsplit('.', 1)[1]}"
                filepath = os.path.join('uploads', filename)
                file.save(filepath)

                # Upload lên Cloudinary từ file local
                upload_result = cloudinary.uploader.upload(filepath,
                    public_id=f"health_analysis/{filename}",
                    folder="health_checker")
                file_url = upload_result['secure_url']

                # Phân tích với AI (sử dụng file local)
                text_prompt = "Hãy phân tích tình trạng thể chất của người trong bức ảnh này một cách khách quan và chuyên nghiệp. Hãy đưa ra nhận xét về các yếu tố như: tư thế, dáng người, cân nặng ước tính, và các dấu hiệu thể chất có thể quan sát được. Đưa ra những gợi ý và lời khuyên hữu ích để cải thiện sức khỏe nếu cần thiết. Hãy giữ giọng điệu tích cực và mang tính xây dựng."
                result = analyze_text_with_image(text_prompt, filepath)

                # Lưu vào database với Cloudinary URL
                user = User.query.filter_by(username=session['username']).first()
                analysis = HealthAnalysis(
                    email=user.email,
                    input=file_url,
                    output=result
                )
                db.session.add(analysis)
                db.session.commit()

                # Xóa file local sau khi đã upload xong
                os.remove(filepath)

                return render_template('health_analysis.html', health_analysis_result=result)

            except Exception as e:
                print(f"Error: {str(e)}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash('Có lỗi xảy ra khi xử lý file')
                return redirect(request.url)
    
    # Thêm return cho phương thức GET
    return render_template('health_analysis.html')

@app.route('/ai_doctor')
def ai_doctor():
    # Return cho route ai_doctor
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
        return jsonify({"result": "Lỗi: Không tìm thấy tệp âm thanh."}), 400

    audio_file = request.files['audio']
    try:
        # Lưu file audio vào uploads trước
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"audio_{timestamp}.webm"
        filepath = os.path.join('uploads', filename)
        audio_file.save(filepath)

        # Upload lên Cloudinary từ file local
        upload_result = cloudinary.uploader.upload(filepath,
            resource_type="video",
            public_id=f"ai_doctor/{filename}",
            folder="health_checker")
        audio_url = upload_result['secure_url']

        # Phân tích audio (sử dụng file local)
        analysis_result = analyze_audio_with_gemini(filepath)

        if analysis_result:
            # Tạo audio response từ ElevenLabs
            audio_stream = stream_text_to_speech(analysis_result)
            
            user = User.query.filter_by(username=session['username']).first()
            analysis = AiDoctor(
                email=user.email,
                input=audio_url,
                output=analysis_result
            )
            db.session.add(analysis)
            db.session.commit()

            # Xóa file local sau khi đã upload xong
            os.remove(filepath)

            return jsonify({
                "result": analysis_result,
                "stream_url": url_for('stream_audio', result=analysis_result)
            })
        else:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"result": "Lỗi: Không thể phân tích âm thanh."}), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"result": "Lỗi: Không thể xử lý tệp âm thanh."}), 500

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
                         ai_doctor_analyses=ai_doctor_analyses,
                         timedelta=timedelta,
                         session=session)

# Thêm route để phục vụ các file tải lên
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def add_column_if_not_exists():
    try:
        # Lấy inspector từ engine của database
        inspector = inspect(db.engine)
        
        # Lấy danh sách các cột hiện có trong bảng user
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        # Kiểm tra nếu cột verified chưa tồn tại
        if 'verified' not in columns:
            # Tạo và thực thi câu lệnh ALTER TABLE
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE user ADD COLUMN verified BOOLEAN DEFAULT FALSE')
                conn.commit()
            print("Đã thêm cột 'verified' vào bảng user")
        else:
            print("Cột 'verified' đã tồn tại trong bảng user")
            
    except Exception as e:
        print(f"Lỗi khi kiểm tra/thêm cột: {str(e)}")

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)