import os
import pandas as pd
import pyodbc
import io
import json
import datetime
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Fetch environment variables
load_dotenv()  # Load environment variables from .env file

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")
sas_token = os.getenv("AZURE_SAS_TOKEN")
if not sas_token:
    raise ValueError("Error: AZURE_SAS_TOKEN environment variable not set.")

account_url = "https://devopstutorialstorageuba.blob.core.windows.net"

DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_TABLE_NAME = "Transactions"

# SQL Server Connection string
conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}"

DEPLOYMENT_LOG_FILE = "deployment_log.json"

def update_deployment_log(new_data):
    """Append new deployment data to a JSON log file as a list of deployments."""
    log_data = {"deployments": []}  # Default structure

    # Check if the deployment log file exists and load existing data
    if os.path.exists(DEPLOYMENT_LOG_FILE):
        with open(DEPLOYMENT_LOG_FILE, "r") as file:
            try:
                log_data = json.load(file)
            except json.JSONDecodeError:
                print("Warning: Corrupted JSON file, resetting log.")

    # Ensure 'deployments' key exists and is a list
    if "deployments" not in log_data or not isinstance(log_data["deployments"], list):
        log_data["deployments"] = []

    # Append the new deployment entry
    log_data["deployments"].append(new_data)

    # Write updated log data back to the file
    with open(DEPLOYMENT_LOG_FILE, "w") as file:
        json.dump(log_data, file, indent=4)

    print("Deployment log updated successfully.")

def fetch_csv_from_blob():
    """Retrieve CSV files from Azure Blob Storage and return a list of dataframes."""
    try:
        blob_service_client = BlobServiceClient(account_url, credential=sas_token)
        container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER_NAME)

        dataframes = []
        blobs = list(container_client.list_blobs())

        if not blobs:
            print("No files found in Blob Storage.")
            return dataframes
        
        for blob in blobs:
            if blob.name.endswith(".csv"):
                blob_client = container_client.get_blob_client(blob.name)
                csv_content = blob_client.download_blob().readall().decode('utf-8')

                # Convert CSV content to Pandas DataFrame
                df = pd.read_csv(io.StringIO(csv_content))
                df["source_file"] = blob.name  # Track source file in the database
                dataframes.append(df)
        
        print(f"Successfully fetched {len(dataframes)} CSV files from Blob Storage.")
        return dataframes

    except Exception as e:
        print(f"Error fetching files from Blob Storage: {e}")
        return []

def insert_data_into_db(dataframes):
    """Insert data from CSV files into Azure SQL Database."""
    rows = 0
    inserted_records = []
    if not dataframes:
        print("No data to insert into the database.")
        return
    
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            for df in dataframes:
                for _, row in df.iterrows():
                    cursor.execute(f"""
                        INSERT INTO {DB_TABLE_NAME} (transaction_id, customer_name, amount, currency, transaction_date)
                        VALUES (?, ?, ?, ?, ?)
                    """, row["transaction_id"], row["customer_name"], row["amount"], row["currency"], row["transaction_date"])
                    rows += 1

            conn.commit()

            # Generate a timestamp in UTC format
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            # Update deployment log
            inserted_records.append({
                "inserted_rows": rows,
                "timestamp": timestamp
            })
            update_deployment_log({"inserted_records": inserted_records})
            
            print("Data inserted successfully!")
        


    except Exception as e:
        print(f"Error inserting data into database: {e}")
        return []


if __name__ == "__main__":
    dataframes = fetch_csv_from_blob()
    if dataframes:
        insert_data_into_db(dataframes)
    else:
        print("No CSV files found in Blob Storage.")