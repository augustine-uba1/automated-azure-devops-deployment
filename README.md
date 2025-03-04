# Automated Deployment & Data Processing Pipeline

## Overview

This project implements an end-to-end CI/CD pipeline using **Azure DevOps**, **Azure Blob Storage**, and **Azure SQL Database** to automate the deployment and data processing of financial transactions.

### Key Features:

1. **CI/CD Pipeline (Azure DevOps - YAML)**
   - Build pipeline triggers on a merge to `main` branch.
   - Release pipeline automates deployment and data processing.
2. **Smoke Test**
   - Verifies database connectivity before proceeding with deployment.
3. **File Upload to Blob Storage**
   - Uploads financial CSV files to Azure Blob Storage.
4. **Data Processing & Ingestion**
   - Reads the uploaded files and inserts data into Azure SQL Database.
5. **Release Notes Generation**
   - Summarizes deployment changes and stores them in Blob Storage.
6. **Email Notification**
   - Sends an email with release notes upon successful deployment.

## Project Structure

```
financial-data-pipeline/
│── azure-pipelines/
│   ├── build-pipeline.yml  # Build pipeline definition
│   ├── release-pipeline.yml  # Release pipeline definition
│── data/
│   ├── transactions_sample.csv  # Sample CSV files
│── scripts/
│   ├── smoke_test.py  # Check database availability
│   ├── upload_to_blob.py  # Upload CSV files to Blob Storage
│   ├── process_data.py  # Read Blob & Insert Data into Database
│   ├── generate_release_note.py  # Generate deployment notes
│   ├── send_email.py  # Send email with release note
│── README.md  # Project documentation
```

## Setup Instructions

### 1. **Configure Azure Resources**

Ensure the following resources are set up:

- **Azure SQL Database** (Create a database and table to store transaction data)
- **Azure Blob Storage** (Create two containers: one for CSV files, one for release notes)
- **SendGrid Email API** (For email notifications)

### 2. **Set Environment Variables in Azure DevOps**

Add these variables in Azure DevOps pipeline settings:

- **Database Credentials:**
  - `DB_SERVER` = `your-database-server.database.windows.net`
  - `DB_NAME` = `your-database-name`
  - `DB_USER` = `your-database-username`
  - `DB_PASSWORD` = `your-database-password`
  - `DB_TABLE_NAME` = `your-table-name`
- **Azure Storage:**
  - `AZURE_STORAGE_CONNECTION_STRING` = `your-connection-string`
  - `AZURE_BLOB_CONTAINER_NAME` = `your-container-name`
  - `AZURE_RELEASE_NOTES_CONTAINER` = `your-container-for-release-notes`
- **Email Notification:**
  - `SENDGRID_API_KEY` = `your-sendgrid-api-key`
  - `EMAIL_SENDER` = `your-email@example.com`
  - `EMAIL_RECIPIENT` = `recipient@example.com`

### 3. **Run the Pipeline**

1. Commit the project to **GitHub**.
2. Merge changes into `main` to trigger the **Build Pipeline**.
3. Approve the **Release Pipeline** to:
   - Perform a **smoke test** on the database.
   - Upload files to **Azure Blob Storage**.
   - Process data and insert it into **Azure SQL Database**.
   - Generate **release notes** and store them in Blob Storage.
   - Send a **release notification email**.

### 4. **Verify Deployment**

- Check Azure Blob Storage for uploaded files and release notes.
- Verify the database table contains newly inserted data.
- Confirm that the email notification is received.

## Next Steps

- Add unit tests for data validation.
- Implement monitoring and alerting for failures.
- Automate infrastructure provisioning using Terraform.

## Useful Links
- [Azure Pipeline Tasks ](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-pipeline-artifact-v1?view=azure-pipelines)
- [Azure Define Pipeline Variables](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops&tabs=yaml%2Cbatch)

## License

MIT License

