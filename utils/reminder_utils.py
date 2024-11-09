from datetime import datetime, timedelta
from flask_mail import Message
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def send_reminder_email(reminder, app, mail):
    """Gửi email nhắc nhở cho người dùng"""
    try:
        msg = Message(
            subject=f'Nhắc nhở: {reminder.title}',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[reminder.user_email]
        )
        
        msg.html = f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #007bff;">Nhắc nhở sức khỏe</h2>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                    <h3 style="color: #333;">{reminder.title}</h3>
                    <p style="color: #666;">{reminder.description}</p>
                    <p style="color: #666;">
                        <strong>Thời gian:</strong> {reminder.time.strftime('%H:%M')}
                    </p>
                </div>
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    Email này được gửi tự động từ Health Checker.
                </p>
            </div>
        '''
        
        mail.send(msg)
        logger.info(f"Sent reminder email to {reminder.user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending reminder email: {str(e)}")
        return False

def init_reminder_scheduler(app, mail, HealthReminder):
    """Khởi tạo scheduler cho hệ thống nhắc nhở"""
    def check_and_send_reminders():
        with app.app_context():
            try:
                current_time = datetime.now().time()
                current_date = datetime.now().date()
                
                # Lấy các nhắc nhở trong khoảng 5 phút gần đây
                reminders = HealthReminder.query.filter(
                    HealthReminder.is_active == True,
                    HealthReminder.time <= current_time,
                    HealthReminder.time >= (datetime.now() - timedelta(minutes=5)).time(),
                    HealthReminder.start_date <= current_date,
                    (HealthReminder.end_date.is_(None) | (HealthReminder.end_date >= current_date))
                ).all()
                
                for reminder in reminders:
                    send_reminder_email(reminder, app, mail)
                    
            except Exception as e:
                logger.error(f"Error in check_and_send_reminders: {str(e)}")
    
    # Thêm job vào scheduler
    scheduler.add_job(
        check_and_send_reminders, 
        'interval', 
        minutes=5,
        id='health_reminder_job'
    )
    
    # Khởi động scheduler nếu chưa chạy
    if not scheduler.running:
        scheduler.start()
        logger.info("Reminder scheduler started")

def shutdown_scheduler():
    """Tắt scheduler an toàn"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Reminder scheduler shutdown") 