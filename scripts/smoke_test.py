import pyodbc
import os
import sys
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
if not DB_SERVER or not DB_NAME or not DB_USER or not DB_PASSWORD:
    raise ValueError("Error: AZURE_SAS_TOKEN environment variable not set.")

# # Fetch database credentials from environment variables
# DB_SERVER = "devops-austine.database.windows.net"
# DB_NAME = "devops-db"
# DB_USER = "devops-admin"
# DB_PASSWORD = "Password12345678!"

# DB_SERVER = os.getenv("devops-austine.database.windows.net")
# DB_NAME = os.getenv("devops-db")
# DB_USER = os.getenv("devops-admin")
# DB_PASSWORD = os.getenv("Password12345678!")

# Connection string
conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}"

def check_database():
    """Check if the database is accessible."""
    try:
        with pyodbc.connect(conn_str, timeout=5) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    print("Database connection successful!")
                    return 1
                else:
                    print("Unexpected database response.")
                    return 0
    except Exception as e:
        print(f"Database connection failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_database())
