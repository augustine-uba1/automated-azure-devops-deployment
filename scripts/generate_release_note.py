import os
import json
from datetime import datetime, timezone
from datetime import timezone
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_RELEASE_NOTES_CONTAINER = os.getenv("AZURE_RELEASE_NOTES_CONTAINER")
sas_token = os.getenv("AZURE_SAS_RELEASE_NOTE")
if not sas_token:
    raise ValueError("Error: AZURE_SAS_TOKEN environment variable not set.")

account_url = "https://devopstutorialstorageuba.blob.core.windows.net"

DEPLOYMENT_LOG_FILE = "deployment_log.json"

def load_deployment_metadata():
    """Load deployment metadata from deployment_log.json."""
    try:
        if os.path.exists(DEPLOYMENT_LOG_FILE):
            with open(DEPLOYMENT_LOG_FILE, "r", encoding="utf-8") as file:
                log_data = json.load(file)
            
            # Ensure deployments key exists
            deployments = log_data.get("deployments", [])
            if not deployments:
                print("Warning: No deployments found in deployment log.")
                return {"message": "No deployment metadata found."}

            latest_uploaded_files = []
            latest_inserted_records = []

            # Find the most recent deployment that contains uploaded_files
            for deployment in reversed(deployments):  # Start from the latest
                if "uploaded_files" in deployment and deployment["uploaded_files"]:
                    latest_uploaded_files = deployment["uploaded_files"]
                    break  # Stop at the first match

            # Find the most recent deployment that contains inserted_records
            for deployment in reversed(deployments):
                if "inserted_records" in deployment and deployment["inserted_records"]:
                    latest_inserted_records = deployment["inserted_records"]
                    break  # Stop at the first match

            return {
                "uploaded_files": latest_uploaded_files,
                "inserted_records": latest_inserted_records
            }
        
        else:
            print("Warning: No deployment_log.json found.")
            return {"message": "No deployment metadata found."}
        
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from deployment_log.json.")
        return {"message": "Corrupt deployment metadata."}
    
def generate_release_note():
    """Generate a release note summarizing deployment changes."""
    deployment_metadata = load_deployment_metadata()
    timestamp = datetime.now(timezone.utc).isoformat()

    # Extract uploaded files and inserted records
    uploaded_files = deployment_metadata.get("uploaded_files", [])
    inserted_records = deployment_metadata.get("inserted_records", [])

    # Format inserted records
    inserted_summary = ""
    for record in inserted_records:
        inserted_summary += f"- {record['inserted_rows']} rows inserted at {record['timestamp']}\n"


    # Construct release note content
    release_note_content = f"""
    Release Notes - {timestamp}
    ==================================

    Files Uploaded and Rows inserted in this release:
    ------------------------

    ✅ Uploaded Files to Blob Storage:
    {json.dumps(uploaded_files, indent=4, ensure_ascii=False) if uploaded_files else "No files uploaded."}

    ✅ Database Insertions:
    {inserted_summary if inserted_records else "No data inserted."}

    End of Release Notes.
    """

    release_note_filename = f"release_note_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.txt"


    # Save release note locally
    with open(release_note_filename, "w", encoding="utf-8") as file:
        file.write(release_note_content)

    print(f"Release note saved: {release_note_filename}")  # Debugging print

    return release_note_filename, release_note_content

def upload_release_note_to_blob(filename):
    """Upload the generated release note to Azure Blob Storage."""
    try:
        blob_service_client = BlobServiceClient(account_url, credential=sas_token)
        container_client = blob_service_client.get_container_client(AZURE_RELEASE_NOTES_CONTAINER)

        print(f"Uploading release note: {filename} to Blob Storage...")
        with open(filename, "rb") as data:
            container_client.upload_blob(name=filename, data=data, overwrite=True)

        print("Release note uploaded successfully.")
    except Exception as e:
        print(f"Error uploading release note: {e}")

# Run the function to generate release notes
if __name__ == "__main__":
    filename, _ = generate_release_note()
    upload_release_note_to_blob(filename)