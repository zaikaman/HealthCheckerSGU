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
        
        headers = {
            'X-Priority': '1',
            'X-MSMail-Priority': 'High',
            'Importance': 'High'
        }
        
        msg = Message(
            subject='Xác nhận tài khoản Health Checker',
            recipients=[to_email],
            headers=headers
        )
        
        msg.html = f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #007bff;">Xác nhận tài khoản Health Checker của bạn</h2>
                <p>Xin chào,</p>
                <p>Cảm ơn bạn đã đăng ký tài khoản trên Health Checker. Để hoàn tất quá trình đăng ký, vui lòng xác nhận địa chỉ email của bạn bằng cách nhấp vào nút bên dưới:</p>
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
                <p style="word-break: break-all;">{confirm_url}</p>
                <p><strong>Lưu ý:</strong> Link xác nhận này sẽ hết hạn sau 24 giờ.</p>
                <hr style="margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">Email này được gửi tự động từ Health Checker. Vui lòng không trả lời email này.</p>
            </div>
        '''
        
        msg.body = f'''
            Xác nhận tài khoản Health Checker của bạn

            Xin chào,

            Cảm ơn bạn đã đăng ký tài khoản trên Health Checker. Để hoàn tất quá trình đăng ký, vui lòng truy cập đường link sau:

            {confirm_url}

            Link xác nhận này sẽ hết hạn sau 24 giờ.

            Trân trọng,
            Health Checker Support Team
        '''
        
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False