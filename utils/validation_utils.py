import re

def is_valid_email(email):
    """
    Kiểm tra tính hợp lệ của địa chỉ email sử dụng regex
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email)) 