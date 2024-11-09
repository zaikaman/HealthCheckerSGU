from datetime import datetime, timedelta
from flask_mail import Message
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import pytz
import traceback

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

# Thêm timezone Việt Nam
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

def send_reminder_email(reminder, app, mail):
    """Gửi email nhắc nhở cho người dùng"""
    try:
        # Kiểm tra tần suất gửi
        current_date = datetime.now().date()
        should_send = False
        
        if reminder.frequency == 'daily':
            should_send = True
        elif reminder.frequency == 'weekly' and current_date.weekday() == reminder.start_date.weekday():
            should_send = True
        elif reminder.frequency == 'monthly' and current_date.day == reminder.start_date.day:
            should_send = True
            
        if not should_send:
            return False

        # Tạo nội dung email
        reminder_types = {
            'medicine': 'Uống thuốc',
            'exercise': 'Tập thể dục',
            'checkup': 'Khám định kỳ'
        }
        
        msg = Message(
            subject=f'Nhắc nhở {reminder_types.get(reminder.reminder_type, "")}: {reminder.title}',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[reminder.user_email]
        )
        
        msg.html = f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #007bff;">Nhắc nhở {reminder_types.get(reminder.reminder_type, "")}</h2>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                    <h3 style="color: #333;">{reminder.title}</h3>
                    <p style="color: #666;">{reminder.description}</p>
                    <p style="color: #666;">
                        <strong>Thời gian:</strong> {reminder.time.strftime('%H:%M')}
                        <br>
                        <strong>Tần suất:</strong> {reminder.frequency}
                    </p>
                </div>
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    Email này được gửi tự động từ Health Checker.
                    <br>
                    Thời gian gửi: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
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
                # Lấy thời gian hiện tại theo giờ Việt Nam
                current_time = datetime.now(vietnam_tz)
                logger.info(f"Checking reminders at {current_time}")
                
                # Lấy tất cả nhắc nhở đang active
                reminders = HealthReminder.query.filter(
                    HealthReminder.is_active == True,
                    HealthReminder.start_date <= current_time.date(),
                    (HealthReminder.end_date.is_(None) | (HealthReminder.end_date >= current_time.date()))
                ).all()
                
                logger.info(f"Found {len(reminders)} active reminders")
                
                for reminder in reminders:
                    logger.info(f"Checking reminder: {reminder.title}")
                    
                    # Chuyển đổi reminder time sang datetime với timezone
                    reminder_datetime = datetime.combine(current_time.date(), reminder.time)
                    reminder_datetime = vietnam_tz.localize(reminder_datetime)
                    
                    logger.info(f"Reminder time: {reminder_datetime.time()}, Current time: {current_time.time()}")
                    
                    # Kiểm tra thời gian
                    if (current_time.hour == reminder_datetime.hour and 
                        current_time.minute == reminder_datetime.minute):
                        
                        logger.info(f"Time match found for reminder: {reminder.title}")
                        
                        # Kiểm tra tần suất
                        should_send = False
                        if reminder.frequency == 'daily':
                            should_send = True
                            logger.info("Daily reminder - should send")
                        elif reminder.frequency == 'weekly' and current_time.weekday() == reminder.start_date.weekday():
                            should_send = True
                            logger.info("Weekly reminder - should send")
                        elif reminder.frequency == 'monthly' and current_time.day == reminder.start_date.day:
                            should_send = True
                            logger.info("Monthly reminder - should send")
                            
                        if should_send:
                            logger.info(f"Attempting to send email for reminder: {reminder.title}")
                            success = send_reminder_email(reminder, app, mail)
                            if success:
                                logger.info(f"Successfully sent reminder email to {reminder.user_email}")
                            else:
                                logger.error(f"Failed to send reminder email to {reminder.user_email}")
                    else:
                        logger.debug(f"Time mismatch - Reminder: {reminder_datetime.time()}, Current: {current_time.time()}")
                    
            except Exception as e:
                logger.error(f"Error in check_and_send_reminders: {str(e)}")
                logger.error(traceback.format_exc())
    
    # Chạy kiểm tra mỗi phút
    scheduler.add_job(
        check_and_send_reminders, 
        'interval', 
        minutes=1,
        id='health_reminder_job'
    )
    
    if not scheduler.running:
        scheduler.start()
        logger.info("Reminder scheduler started")

def shutdown_scheduler():
    """Tắt scheduler an toàn"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Reminder scheduler shutdown") 