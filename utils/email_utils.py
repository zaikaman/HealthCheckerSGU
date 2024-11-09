def generate_confirmation_token(email, app):
    from datetime import datetime, timedelta
    import jwt
    
    return jwt.encode(
        {'email': email, 'exp': datetime.utcnow() + timedelta(hours=24)},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def send_confirmation_email(to_email, token, app, mail):
    from flask import url_for
    from flask_mail import Message
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        confirm_url = url_for('confirm_email', token=token, _external=True)
        
        msg = Message('Xác nhận tài khoản',
                     sender=app.config['MAIL_USERNAME'],
                     recipients=[to_email])
        
        msg.html = f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #007bff;">Xác nhận tài khoản của bạn</h2>
                <p>Cảm ơn bạn đã đăng ký tài khoản. Để hoàn tất quá trình đăng ký, vui lòng click vào nút bên dưới:</p>
                <a href="{confirm_url}" 
                   style="display: inline-block; 
                          background-color: #007bff; 
                          color: white; 
                          padding: 10px 20px; 
                          text-decoration: none; 
                          border-radius: 5px; 
                          margin: 20px 0;">
                    Xác nhận tài khoản
                </a>
                <p>Hoặc copy và paste đường link sau vào trình duyệt:</p>
                <p>{confirm_url}</p>
                <p>Link xác nhận này sẽ hết hạn sau 24 giờ.</p>
            </div>
        '''
        
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False 