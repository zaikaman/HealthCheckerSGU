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
from flask_mail import Mail
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from utils.email_utils import generate_confirmation_token, send_confirmation_email
from utils.file_utils import allowed_file, add_column_if_not_exists
from utils.audio_utils import generate_text_to_speech
from utils.validation_utils import is_valid_email
import traceback
from utils.reminder_utils import init_reminder_scheduler, shutdown_scheduler
import atexit
import pytz
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from contextlib import contextmanager
import time

app = Flask(__name__)

vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

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
app.db = db  # Thêm db vào app instance

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
    input = db.Column(db.Text, nullable=False)  # User's audio input
    output = db.Column(db.Text, nullable=False)  # AI text response
    response_audio = db.Column(db.Text, nullable=True)  # ElevenLabs audio URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthReminder(db.Model):
    __tablename__ = 'tbl_health_reminders'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    reminder_type = db.Column(db.String(50), nullable=False)  # medicine, exercise, checkup
    frequency = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly
    time = db.Column(db.Time, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<HealthReminder {self.title}>'

# Tạo cơ sở dữ liệu nếu chưa tồn tại
with app.app_context():
    db.create_all()
    add_column_if_not_exists(db)

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
app.config['MAIL_DEFAULT_SENDER'] = ('Health Checker Support', 'thinhgpt1706@gmail.com')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# Khởi tạo Mail
mail = Mail(app)

# Thêm logging để debug
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Thêm biến global để theo dõi trạng thái scheduler
_scheduler_initialized = False

def initialize_scheduler():
    global _scheduler_initialized
    if not _scheduler_initialized:
        init_reminder_scheduler(app, mail, HealthReminder)
        _scheduler_initialized = True
        logger.info("Scheduler initialized for the first time")

# Sau khi khởi tạo app, db, mail
initialize_scheduler()

# Thêm route để kiểm tra trạng thái scheduler
@app.route('/scheduler-status')
def scheduler_status():
    global _scheduler_initialized
    try:
        from utils.reminder_utils import scheduler
        is_running = scheduler.running
        jobs = len(scheduler.get_jobs())
        return {
            'initialized': _scheduler_initialized,
            'running': is_running,
            'jobs': jobs,
            'next_run': scheduler.get_jobs()[0].next_run_time.strftime('%Y-%m-%d %H:%M:%S') if jobs > 0 else None
        }
    except Exception as e:
        logger.error(f"Error checking scheduler status: {str(e)}")
        return {'error': str(e)}

# Khi cần tắt app
@atexit.register
def shutdown():
    shutdown_scheduler()

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
        try:
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
                    
                    # Sa lại phần gửi email xác nhận
                    token = generate_confirmation_token(email, app)
                    if not send_confirmation_email(email, token, app, mail):
                        logger.error("Failed to send confirmation email")
                        flash('Có lỗi xảy ra khi gửi email xác nhận. Vui lòng thử lại.')
                        return redirect(url_for('signup'))
                    
                    logger.info(f"Confirmation email sent to {email}")
                    flash("Tài khoản đã được tạo! Vui lòng kiểm tra email để xác nhận.", "success")
                    return redirect(url_for('login'))
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error during signup: {str(e)}")
                    logger.error(traceback.format_exc())
                    flash('Có lỗi xảy ra. Vui lòng thử lại.')
                    return redirect(url_for('signup'))
        
        except Exception as e:
            logger.error(f"Error in signup: {str(e)}")
            logger.error(traceback.format_exc())
            flash('Có lỗi xảy ra. Vui lòng thử lại.')
            return redirect(url_for('signup'))
    
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
                # Lưu file vào uploads trưc
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

# Thêm decorator để retry khi mất kết nối
def retry_on_db_error(max_retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    if "Lost connection" in str(e) and retries < max_retries - 1:
                        retries += 1
                        time.sleep(delay)
                        # Reconnect to database
                        db.session.rollback()
                        db.session.remove()
                    else:
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/analyze_audio', methods=['POST'])
@retry_on_db_error()
def analyze_audio():
    if 'audio' not in request.files:
        return jsonify({"result": "Lỗi: Không tìm thấy tệp âm thanh."}), 400

    audio_file = request.files['audio']
    filepath = None
    audio_response_path = None
    
    try:
        # Save user's audio input
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"audio_{timestamp}.mp3"
        filepath = os.path.join('uploads', filename)
        audio_file.save(filepath)

        # Upload user's audio to Cloudinary
        upload_result = cloudinary.uploader.upload(filepath,
            resource_type="video",
            public_id=f"ai_doctor/{filename}",
            folder="health_checker")
        audio_url = upload_result['secure_url']

        # Analyze audio
        analysis_result = analyze_audio_with_gemini(filepath)

        if analysis_result:
            # Generate ElevenLabs audio response
            audio_data = generate_text_to_speech(analysis_result, client)
            
            if audio_data:
                # Save ElevenLabs audio response
                audio_response_filename = f"response_{timestamp}.mp3"
                audio_response_path = os.path.join('uploads', audio_response_filename)
                
                with open(audio_response_path, 'wb') as f:
                    f.write(audio_data)

                # Upload ElevenLabs audio to Cloudinary
                response_upload_result = cloudinary.uploader.upload(
                    audio_response_path,
                    resource_type="video",
                    public_id=f"ai_doctor/response_{audio_response_filename}",
                    folder="health_checker"
                )
                response_audio_url = response_upload_result['secure_url']

                # Save to database
                try:
                    with db.session.begin_nested():
                        user = User.query.filter_by(username=session['username']).first()
                        if not user:
                            raise ValueError("User not found")
                            
                        analysis = AiDoctor(
                            email=user.email,
                            input=audio_url,
                            output=analysis_result,
                            response_audio=response_audio_url
                        )
                        db.session.add(analysis)
                    db.session.commit()
                    
                except Exception as db_error:
                    logger.error(f"Database error: {str(db_error)}")
                    db.session.rollback()

                return jsonify({
                    "result": analysis_result,
                    "audio_url": response_audio_url
                })

        return jsonify({"result": analysis_result})
        
    except Exception as e:
        logger.error(f"Error in analyze_audio: {str(e)}")
        return jsonify({"result": "Lỗi: Không thể xử lý tệp âm thanh."}), 500
        
    finally:
        # Clean up temporary files
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        if audio_response_path and os.path.exists(audio_response_path):
            os.remove(audio_response_path)
        db.session.remove()

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

@app.route('/reminders', methods=['GET', 'POST'])
def reminders():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            reminder_type = request.form['type']
            frequency = request.form['frequency']
            time_str = request.form['time']
            
            # Không cần chuyển đổi timezone nữa, lưu trực tiếp thời gian local
            time = datetime.strptime(time_str, '%H:%M').time()
            
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form['end_date'] else None

            reminder = HealthReminder(
                user_email=user.email,
                title=title,
                description=description,
                reminder_type=reminder_type,
                frequency=frequency,
                time=time,  # Lưu trực tiếp thời gian local
                start_date=start_date,
                end_date=end_date,
                is_active=True,
                created_at=datetime.now()  # Sử dụng thời gian local
            )
            
            db.session.add(reminder)
            db.session.commit()
            
            logger.info(f"Created new reminder for user {user.email}")
            flash('Đã tạo nhắc nhở mới thành công!', 'success')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating reminder: {str(e)}")
            flash('Có lỗi xảy ra khi tạo nhắc nhở. Vui lòng thử lại.', 'danger')
            
        return redirect(url_for('reminders'))
        
    # Lấy danh sách nhắc nhở
    reminders = HealthReminder.query.filter_by(
        user_email=user.email,
        is_active=True
    ).order_by(HealthReminder.time).all()
    
    return render_template('reminders.html', reminders=reminders)

@app.route('/edit_reminder/<int:id>', methods=['POST'])
def edit_reminder(id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    try:
        reminder = HealthReminder.query.get_or_404(id)
        user = User.query.filter_by(username=session['username']).first()
        
        if reminder.user_email != user.email:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
        reminder.title = request.form['title']
        reminder.description = request.form['description']
        reminder.reminder_type = request.form['type']
        reminder.frequency = request.form['frequency']
        
        # Lưu trực tiếp thời gian local
        time_str = request.form['time']
        reminder.time = datetime.strptime(time_str, '%H:%M').time()
        
        reminder.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        reminder.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form['end_date'] else None
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cập nhật thành công'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating reminder: {str(e)}")
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra'}), 500

@app.route('/delete_reminder/<int:id>', methods=['POST'])
def delete_reminder(id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    try:
        reminder = HealthReminder.query.get_or_404(id)
        user = User.query.filter_by(username=session['username']).first()
        
        # Verify ownership
        if reminder.user_email != user.email:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
        reminder.is_active = False  # Soft delete
        db.session.commit()
        return jsonify({'success': True, 'message': 'Xóa thành công'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting reminder: {str(e)}")
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra'}), 500

@app.route('/search_reminders')
def search_reminders():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    try:
        user = User.query.filter_by(username=session['username']).first()
        query = request.args.get('query', '').strip()
        reminder_type = request.args.get('type', '')
        
        # Base query
        reminders_query = HealthReminder.query.filter_by(
            user_email=user.email,
            is_active=True
        )
        
        # Add search conditions
        if query:
            reminders_query = reminders_query.filter(
                (HealthReminder.title.ilike(f'%{query}%')) |
                (HealthReminder.description.ilike(f'%{query}%'))
            )
            
        if reminder_type:
            reminders_query = reminders_query.filter_by(reminder_type=reminder_type)
            
        reminders = reminders_query.order_by(HealthReminder.time).all()
        
        # Format reminders for JSON response
        reminders_data = []
        for reminder in reminders:
            reminders_data.append({
                'id': reminder.id,
                'title': reminder.title,
                'description': reminder.description,
                'type': reminder.reminder_type,
                'frequency': reminder.frequency,
                'time': reminder.time.strftime('%H:%M'),
                'start_date': reminder.start_date.strftime('%Y-%m-%d'),
                'end_date': reminder.end_date.strftime('%Y-%m-%d') if reminder.end_date else ''
            })
            
        return jsonify({'success': True, 'reminders': reminders_data})
        
    except Exception as e:
        logger.error(f"Error searching reminders: {str(e)}")
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra'}), 500

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    port = int(os.environ.get("PORT", 5000))
    
    # # Chỉ khởi chạy scheduler trong tiến trình chính
    # if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    #     initialize_scheduler()
    
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)