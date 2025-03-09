import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
sas_token = os.getenv("AZURE_SAS_TOKEN")
if not sas_token:
    raise ValueError("Error: AZURE_SAS_TOKEN environment variable not set.")

account_url = "https://devopstutorialstorageuba.blob.core.windows.net"
container_name = 'devops-tutorial-backup'

def get_blob_service_client_sas(sas_token: str) -> BlobServiceClient:
    """Create and return a BlobServiceClient using a SAS token."""
    try:
        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient(account_url, credential=sas_token)
        
        # Create a container client to check permissions on the container
        container_client = blob_service_client.get_container_client(container_name)

        # Test if the SAS token works by listing blobs in the container
        blobs = list(container_client.list_blobs())

        print(f"Blob service client created successfully. Found {len(blobs)} blobs in container '{container_name}'.")
        return blob_service_client    

    except AzureError as e:
        print(f"Failed to create blob service client: {e}")
        return None  # Return None to indicate failure

# message = get_blob_service_client_sas(sas_token =  credential)
# print("Result:", message)

def upload_csv_files(blob_service_client: BlobServiceClient):
    """Upload all CSV files from the 'data' folder (located one level above the script)."""
    try:
        container_client = blob_service_client.get_container_client(container_name)

        # Get the absolute path to the 'data' folder (one level up from the script)
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Path to 'Scripts'
        data_folder = os.path.join(script_dir, "..", "data")  # Move up and into 'data'
        data_folder = os.path.abspath(data_folder)  # Normalize path

        if not os.path.exists(data_folder):
            print(f"Error: Data folder '{data_folder}' not found.")
            return

        # Get all CSV files in the 'data' folder
        csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

        if not csv_files:
            print("No CSV files found in the data folder.")
            return

        for file_name in csv_files:
            blob_name = file_name  # The name of the file in Blob Storage
            file_path = os.path.join(data_folder, file_name)

            print(f"Uploading {file_name} to Azure Blob Storage...")
            with open(file_path, "rb") as data:
                container_client.upload_blob(name=blob_name, data=data, overwrite=True)

            print(f"Successfully uploaded: {file_name}")

    except Exception as e:
        print(f"Error uploading files: {e}")

# Connect to Azure Blob Storage
if __name__ == "__main__":
    blob_service_client = get_blob_service_client_sas(sas_token)

    # Upload all CSV files from the 'data' folder
    if blob_service_client:
        upload_csv_files(blob_service_client)