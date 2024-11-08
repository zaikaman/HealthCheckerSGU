def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_column_if_not_exists(db):
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'verified' not in columns:
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE user ADD COLUMN verified BOOLEAN DEFAULT FALSE')
                conn.commit()
            print("Đã thêm cột 'verified' vào bảng user")
        else:
            print("Cột 'verified' đã tồn tại trong bảng user")
            
    except Exception as e:
        print(f"Lỗi khi kiểm tra/thêm cột: {str(e)}") 