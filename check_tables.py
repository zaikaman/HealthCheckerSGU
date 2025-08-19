import os
import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables
load_dotenv('.env.local')

# PostgreSQL connection
POSTGRES_CONFIG = {
    'dbname': os.getenv('PGDATABASE'),
    'user': os.getenv('PGUSER'),
    'password': os.getenv('PGPASSWORD'),
    'host': os.getenv('PGHOST_UNPOOLED'),
    'sslmode': 'require'
}

def show_tables():
    """Show all tables in the database"""
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()
    
    try:
        # Get list of tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        
        print("\n=== Tables in database ===")
        for table in tables:
            print(f"\n--- Table: {table[0]} ---")
            
            # Get column information
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table[0]}'
            """)
            columns = cur.fetchall()
            print(tabulate(columns, headers=['Column', 'Type', 'Nullable']))
            
            # Get row count
            cur.execute(f'SELECT COUNT(*) FROM "{table[0]}"')
            count = cur.fetchone()[0]
            print(f"\nTotal rows: {count}")
            
            # Show sample data if exists
            if count > 0:
                cur.execute(f'SELECT * FROM "{table[0]}" LIMIT 3')
                rows = cur.fetchall()
                cur.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table[0]}'
                    ORDER BY ordinal_position
                """)
                headers = [col[0] for col in cur.fetchall()]
                print("\nSample data:")
                print(tabulate(rows, headers=headers))
            
            print("\n" + "="*50)
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    show_tables() 