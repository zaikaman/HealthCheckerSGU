from flask_sqlalchemy import SQLAlchemy
import time

def retry_on_db_error(db, max_retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "Lost connection" in str(e) and retries < max_retries - 1:
                        retries += 1
                        time.sleep(delay)
                        db.session.rollback()
                        db.session.remove()
                    else:
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator 