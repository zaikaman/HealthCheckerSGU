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
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.exc import OperationalError
from contextlib import contextmanager
import time
from functools import wraps
import sqlalchemy
from collections import deque
from threading import Lock

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres://neondb_owner:T4cXILdWm1EF@ep-floral-heart-a1qp38z8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'thinhgpt1706@gmail.com'
app.config['MAIL_PASSWORD'] = 'xgxn kjcv haqf sjxz'
app.config['MAIL_DEFAULT_SENDER'] = ('Health Checker Support', 'thinhgpt1706@gmail.com')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    analyses = db.relationship('Analysis', backref='user', lazy=True)

class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FileAnalysis(db.Model):
    __tablename__ = 'tbl_file_analysis'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthAnalysis(db.Model):
    __tablename__ = 'tbl_health_analysis'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AiDoctor(db.Model):
    __tablename__ = 'tbl_ai_doctor'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=False)
    response_audio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthReminder(db.Model):
    __tablename__ = 'tbl_health_reminders'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    reminder_type = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    time = db.Column(db.Time, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def initialize_scheduler():
    """Initialize the reminder scheduler"""
    try:
        init_reminder_scheduler(app, mail, HealthReminder)
    except Exception as e:
        app.logger.error(f"Failed to initialize scheduler: {e}")

# Initialize the app
with app.app_context():
    try:
        db.create_all()
        initialize_scheduler()
    except Exception as e:
        app.logger.error(f"Failed to initialize app: {e}")

# For Vercel serverless function
app.debug = True

# Export the Flask application
application = app 