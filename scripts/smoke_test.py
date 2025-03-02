import pyodbc
import os
import sys

# Fetch database credentials from environment variables
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connection string
conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}"

def check_database():
    """Check if the database is accessible."""
    try:
        with pyodbc.connect(conn_str, timeout=5) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    print("Database connection successful!")
                    return 0
                else:
                    print("Unexpected database response.")
                    return 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_database())
