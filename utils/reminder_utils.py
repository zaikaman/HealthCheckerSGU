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

# Thêm biến global để kiểm tra scheduler đã được khởi tạo chưa
scheduler_initialized = False

# Thêm cache để lưu các reminder đã gửi trong phút hiện tại
sent_reminders = set()

def send_reminder_email(reminder, app, mail, cache_key):
    """Gửi email nhắc nhở cho người dùng"""
    try:
        # Tạo nội dung email
        reminder_types = {
            'medicine': 'Uống thuốc',
            'exercise': 'Tập thể dục',
            'checkup': 'Khám định kỳ'
        }
        
        email_content = f'''
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
        
        msg = Message(
            subject=f'Nhắc nhở {reminder_types.get(reminder.reminder_type, "")}: {reminder.title}',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[reminder.user_email]
        )
        
        msg.html = email_content
        mail.send(msg)
        
        # Lưu cache_key vào sent_reminders
        sent_reminders.add(cache_key)
        
        # Xóa cache cũ (giữ lại cache trong 5 phút)
        current_time = datetime.now()
        old_keys = {k for k in sent_reminders if datetime.strptime(k.split('_')[1], '%Y%m%d%H%M') < current_time - timedelta(minutes=5)}
        sent_reminders.difference_update(old_keys)
        
        logger.info(f"Sent reminder email to {reminder.user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending reminder email: {str(e)}")
        return False

def init_reminder_scheduler(app, mail, HealthReminder):
    """Khởi tạo scheduler cho hệ thống nhắc nhở"""
    global scheduler_initialized
    
    if scheduler_initialized:
        logger.info("Scheduler already initialized, skipping...")
        return
        
    def check_and_send_reminders():
        with app.app_context():
            try:
                # Sử dụng thời gian local
                current_time = datetime.now()
                logger.info(f"[Scheduler] Running check at {current_time}")
                
                reminders = HealthReminder.query.filter(
                    HealthReminder.is_active == True,
                    HealthReminder.start_date <= current_time.date(),
                    (HealthReminder.end_date.is_(None) | (HealthReminder.end_date >= current_time.date()))
                ).all()
                
                logger.info(f"[Scheduler] Found {len(reminders)} active reminders")
                
                for reminder in reminders:
                    logger.info(f"[Scheduler] Processing reminder: {reminder.title}")
                    reminder_datetime = datetime.combine(current_time.date(), reminder.time)
                    
                    if (current_time.hour == reminder_datetime.hour and 
                        current_time.minute == reminder_datetime.minute):
                        
                        cache_key = f"{reminder.id}_{current_time.strftime('%Y%m%d%H%M')}"
                        
                        if cache_key in sent_reminders:
                            logger.info(f"Already sent reminder for {reminder.title} at {current_time.strftime('%Y-%m-%d %H:%M')}")
                            continue
                        
                        if send_reminder_email(reminder, app, mail, cache_key):
                            pass
            except Exception as e:
                logger.error(f"Error in check_and_send_reminders: {str(e)}")
                logger.error(traceback.format_exc())
    
    # Chạy kiểm tra vào mỗi giây thứ 0 của mỗi phút
    job = scheduler.add_job(
        check_and_send_reminders,
        'cron',
        second=0,
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