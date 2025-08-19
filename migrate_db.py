import os
import pymysql
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# MySQL connection (source)
MYSQL_CONFIG = {
    'host': 'o3iyl77734b9n3tg.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
    'user': 'yh2k7r2tjiynygfo',
    'password': 'chsl4bzvipbei6jc',
    'db': 'wk5ybqcvorkax5bp',
    'charset': 'utf8mb4'
}

# PostgreSQL connection (destination)
POSTGRES_CONFIG = {
    'dbname': os.getenv('PGDATABASE'),
    'user': os.getenv('PGUSER'),
    'password': os.getenv('PGPASSWORD'),
    'host': os.getenv('PGHOST_UNPOOLED'),
    'sslmode': 'require'
}

def migrate_table(mysql_cur, pg_cur, table_name, columns, pg_table_name=None):
    """
    Migrate data from MySQL to PostgreSQL
    :param pg_table_name: Optional different table name for PostgreSQL (if different from MySQL)
    """
    print(f"Migrating {table_name}...")
    
    try:
        # Get data from MySQL
        mysql_cur.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = mysql_cur.fetchall()
        
        if not rows:
            print(f"No data found in {table_name}")
            return
        
        # Use different table name for PostgreSQL if specified
        target_table = pg_table_name or table_name
        
        # Prepare for PostgreSQL insert
        columns_str = ', '.join(f'"{col}"' for col in columns)
        
        # Insert into PostgreSQL
        execute_values(
            pg_cur,
            f'INSERT INTO "{target_table}" ({columns_str}) VALUES %s ON CONFLICT DO NOTHING',
            rows
        )
        print(f"Successfully migrated {len(rows)} rows from {table_name} to {target_table}")
        
    except Exception as e:
        print(f"Error migrating {table_name}: {str(e)}")
        raise

def main():
    # Connect to MySQL
    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    mysql_cur = mysql_conn.cursor()
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
    pg_cur = pg_conn.cursor()
    
    try:
        # Migrate users (note the different table name in PostgreSQL)
        migrate_table(
            mysql_cur, pg_cur, 'user',
            ['id', 'username', 'email', 'password', 'verified'],
            pg_table_name='users'
        )
        
        # Migrate analysis
        migrate_table(
            mysql_cur, pg_cur, 'analysis',
            ['id', 'user_id', 'input', 'output', 'created_at']
        )
        
        # Migrate file analysis
        migrate_table(
            mysql_cur, pg_cur, 'tbl_file_analysis',
            ['id', 'email', 'input', 'output', 'created_at']
        )
        
        # Migrate health analysis
        migrate_table(
            mysql_cur, pg_cur, 'tbl_health_analysis',
            ['id', 'email', 'input', 'output', 'created_at']
        )
        
        # Migrate AI doctor
        migrate_table(
            mysql_cur, pg_cur, 'tbl_ai_doctor',
            ['id', 'email', 'input', 'output', 'response_audio', 'created_at']
        )
        
        # Migrate health reminders
        migrate_table(
            mysql_cur, pg_cur, 'tbl_health_reminders',
            ['id', 'user_email', 'title', 'description', 'reminder_type', 
             'frequency', 'time', 'start_date', 'end_date', 'is_active', 'created_at']
        )
        
        # Commit changes
        pg_conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        pg_conn.rollback()
    
    finally:
        mysql_cur.close()
        mysql_conn.close()
        pg_cur.close()
        pg_conn.close()

if __name__ == '__main__':
    main() 