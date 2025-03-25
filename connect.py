import json
import time
import requests
import pandas as pd
from simple_salesforce import Salesforce

# Salesforce credentials
USERNAME = 'your_username'
PASSWORD = 'your_password'
SECURITY_TOKEN = 'your_security_token'
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
DOMAIN = 'login'  # Use 'test' for Sandbox

# Authenticate using simple-salesforce
def authenticate():
    auth_url = f"https://drac.salesforce.com/services/oauth2/token"
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": USERNAME,
        "password": PASSWORD + SECURITY_TOKEN
    }

    response = requests.post(auth_url, data=data)
    if response.status_code == 200:
        auth_response = response.json()
        return auth_response["access_token"], auth_response["instance_url"]
    else:
        raise Exception(f"Authentication Failed: {response.text}")

# Create a Bulk API job
access_token="00DNS00000GYBUW!AQEAQHycw0nKX5nMBCwvQ1SZgItpYCbAv7IrBQxnnthehu8_P5aCLd82zTXWajA1jv6xQVeRjq4k7kl2oDad6GLUJh6u4kAV"

instance_url="https://orgfarm-2d12fabc67-dev-ed.develop.my.salesforce.com"

client_id="3MVG98_Psg5cppyYCmk1gZNC25o00SXpgpodlS29IZ6pXiHkt3xuPa5qIjBTtEgdsiMuIWVN_8F0jnwEtbDh4"


def create_bulk_job(access_token, instance_url, object_name, operation):
    url = f"{instance_url}/services/data/v58.0/jobs/ingest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    job_data = {
        "operation": operation,  # 'insert', 'update', 'delete', etc.
        "object": object_name,
        "contentType": "CSV"
    }
    
    response = requests.post(url, headers=headers, json=job_data)
    
    if response.status_code == 201:
        return response.json()["id"]
    else:
        raise Exception(f"Failed to create job: {response.text}")

# Upload CSV data to the bulk job
def upload_csv_data(access_token, instance_url, job_id, data):
    url = f"{instance_url}/services/data/v58.0/jobs/ingest/{job_id}/batches"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "text/csv",
        "Accept": "application/json"
    }

    response = requests.put(url, headers=headers, data=data.to_csv(index=False))
    
    if response.status_code == 201:
        print("Data uploaded successfully.")
    else:
        raise Exception(f"Failed to upload data: {response.text}")

# Close the job
def close_job(access_token, instance_url, job_id):
    url = f"{instance_url}/services/data/v58.0/jobs/ingest/{job_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    job_update = {"state": "UploadComplete"}
    response = requests.patch(url, headers=headers, json=job_update)
    
    if response.status_code == 200:
        print("Job closed successfully.")
    else:
        raise Exception(f"Failed to close job: {response.text}")

# Check job status
def check_job_status(access_token, instance_url, job_id):
    url = f"{instance_url}/services/data/v58.0/jobs/ingest/{job_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    while True:
        response = requests.get(url, headers=headers)
        job_status = response.json()
        print(f"Job Status: {job_status['state']}")

        if job_status["state"] in ["JobComplete", "Failed", "Aborted"]:
            return job_status
        time.sleep(5)

# Main execution
def main():
    try:
        # Authenticate and get access token
        access_token, instance_url = authenticate()

        # Define Salesforce object and operation
        salesforce_object = "Account"  # Change to the object you need
        operation = "insert"  # 'insert', 'update', 'delete', etc.

        # Create a bulk job
        job_id = create_bulk_job(access_token, instance_url, salesforce_object, operation)
        print(f"Bulk job created: {job_id}")

        # Sample data to upload (Replace with actual data)
        data = pd.DataFrame([
            {"Name": "Test Account 1", "BillingCity": "New York"},
            {"Name": "Test Account 2", "BillingCity": "Los Angeles"}
        ])

        # Upload data
        upload_csv_data(access_token, instance_url, job_id, data)

        # Close the job
        close_job(access_token, instance_url, job_id)

        # Check job status
        job_status = check_job_status(access_token, instance_url, job_id)
        print("Final Job Status:", job_status)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
