# Cleaned sensitive data exposure in app.py
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
from functools import wraps
import sqlalchemy
from collections import deque
from threading import Lock

app = Flask(__name__)

vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# Cấu hình cơ sở dữ liệu
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://yh2k7r2tjiynygfo:chsl4bzvipbei6jc@o3iyl77734b9n3tg.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/wk5ybqcvorkax5bp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'pool_timeout': 30
}

# Initialize ElevenLabs client
class ApiKeyRotator:
    def __init__(self, api_keys):
        self.api_keys = deque(api_keys)
        self.lock = Lock()
    
    def get_next_key(self):
        with self.lock:
            # Get current key
            current_key = self.api_keys[0]
            # Rotate the deque
            self.api_keys.rotate(-1)
            return current_key

# List of API keys
ELEVEN_LABS_API_KEYS = [
    "YOUR-KEY-1",
    "YOUR-KEY-2",
    "YOUR-KEY-3",
]

# Initialize the key rotator
api_key_rotator = ApiKeyRotator(ELEVEN_LABS_API_KEYS)

# Instead of initializing a single client, create a function to get a client with the next key
def get_eleven_labs_client():
    next_key = api_key_rotator.get_next_key()
    return ElevenLabs(api_key=next_key)

analysis_result = ""

# Cấu hình thư mục tải lên
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = 'uploads'

# Kiểm tra đuôi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
app.db = db  # Thêm db vào app instance

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    verified = db.Column(db.Boolean, default=False)

#... rest of file truncated for brevity in this summary
