from datetime import datetime, timedelta, date
from flask_mail import Message
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import pytz
import traceback

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

# Thêm timezone Việt Nam
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# Thêm biến global để kiểm tra scheduler đã được khởi tạo chưa
scheduler_initialized = False

# Thêm cache để lưu các reminder đã gửi trong phút hiện tại
sent_reminders = set()

def send_reminder_email(reminder, app, mail, cache_key):
    """Gửi email nhắc nhở cho người dùng"""
    try:
        with app.app_context():
            # Tạo nội dung email
            reminder_types = {
                'medicine': 'Uống thuốc',
                'exercise': 'Tập thể dục',
                'checkup': 'Khám định kỳ'
            }
            
            msg = Message(
                f'Nhắc nhở: {reminder_types.get(reminder.reminder_type, "")}',
                sender=app.config['MAIL_USERNAME'],
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
                </div>
            '''
            
            mail.send(msg)
            logger.info(f"[Email] Sent reminder email to {reminder.user_email}")
            
    except Exception as e:
        logger.error(f"[Email] Error sending reminder email: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def init_reminder_scheduler(app, mail, HealthReminder):
    """Khởi tạo scheduler cho hệ thống nhắc nhở"""
    global scheduler_initialized
    
    if scheduler_initialized:
        logger.info("Scheduler already initialized, skipping...")
        return
        
    def check_and_send_reminders():
        try:
            current_time = datetime.now(vietnam_tz)
            logger.info(f"[Scheduler] Running check at {current_time}")
            
            # Lấy tất cả reminder đang active
            active_reminders = HealthReminder.query.filter_by(is_active=True).all()
            logger.info(f"[Scheduler] Found {len(active_reminders)} active reminders")
            
            for reminder in active_reminders:
                logger.info(f"[Scheduler] Processing reminder: {reminder.title}")
                logger.info(f"[Scheduler] Reminder time: {reminder.time}")
                logger.info(f"[Scheduler] Current time: {current_time.time()}")
                
                # Kiểm tra thời gian
                reminder_time = reminder.time.replace(tzinfo=vietnam_tz)
                current_time_no_date = current_time.time()
                reminder_time_no_date = reminder_time.time()
                
                time_diff = abs((datetime.combine(date.today(), current_time_no_date) - 
                               datetime.combine(date.today(), reminder_time_no_date)).total_seconds())
                               
                logger.info(f"[Scheduler] Time difference: {time_diff} seconds")
                
                if time_diff <= 60:  # Trong khoảng 1 phút
                    try:
                        send_reminder_email(reminder)
                        logger.info(f"[Scheduler] Email sent successfully for reminder: {reminder.title}")
                    except Exception as e:
                        logger.error(f"[Scheduler] Error sending email: {str(e)}")
                        
        except Exception as e:
            logger.error(f"[Scheduler] Error in check_and_send_reminders: {str(e)}")
            logger.error(traceback.format_exc())
    
    # Chạy kiểm tra mỗi 30 giây
    job = scheduler.add_job(
        check_and_send_reminders, 
        'interval', 
        seconds=30,
        id='health_reminder_job',
        replace_existing=True
    )
    
    if not scheduler.running:
        scheduler.start()
        scheduler_initialized = True
        logger.info(f"[Scheduler] Started with job ID: {job.id}, next run at: {job.next_run_time}")
    
def shutdown_scheduler():
    """Tắt scheduler an toàn"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Reminder scheduler shutdown")