from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import time
import requests
import pandas as pd
from simple_salesforce import Salesforce
import pandas as pd


CLIENT_ID = "3MVG9RGN2EqkAxhKrJ5w8OWd_OuExOPbqsvZKoB_O7wj5U1jgH0y92OlFl8Hf2razPYRetlHOBB6B5F_IKHRX"
CLIENT_SECRET = "228B7A93F92B04BF0F4687F41A3D1C22F8FA6D2ECA0D78A4B879AEDBF77A67DD"
USERNAME = "nitin945737-uabe@force.com"
PASSWORD = "Nitin@321"
SECURITY_TOKEN = "S2Xt1ynuLEp6t6cCBgeXLYTT5" 


app = Flask(__name__)
CORS(app)

@app.route('/create_job',methods=["POST"])
def create_bulk_job():
    access_token=request.form.get("access_token")
    instance_url=request.form.get("instance_url")
    print(instance_url)
    print(access_token)
    object_name=request.form.get("object_name")
    url = f"{instance_url}/services/data/v62.0/jobs/ingest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    job_data = {
        "operation": "insert",  # 'insert', 'update', 'delete', etc.
        "object": object_name,
        "contentType": "CSV",
        "lineEnding":"CRLF"
    }
    
    response = requests.post(url, headers=headers, json=job_data)
    response=response.json()
    print(response)
    return response["id"]

@app.route('/upload_data',methods=["POST"])
def upload_csv_data():
    access_token=request.form.get("access_token")
    instance_url=request.form.get("instance_url")
    job_id=request.form.get("job_id")
    try:
        url = f"{instance_url}/services/data/v62.0/jobs/ingest/{job_id}/batches"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }
        
        
        # data = pd.DataFrame([
        #     {"Name": "Test Account 1", "BillingCity": "New York"},
        #     {"Name": "Test Account 2", "BillingCity": "Los Angeles"}
        # ])
        data = pd.read_csv('googleplaystore.csv')
        response = requests.put(url, headers=headers, data=data.to_csv(index=False))

        print(response)
        if response.status_code==201:
            return jsonify({"message":"file Uploaded"})
        else:
            return jsonify({"messae":"Error while uploading file"})
    except:
        print("a")
        print(response.text)



@app.route('/close_job',methods=["POST"])
def close_job():
    access_token=request.form.get("access_token")
    instance_url=request.form.get("instance_url")
    job_id=request.form.get("job_id")
    url = f"{instance_url}/services/data/v62.0/jobs/ingest/{job_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    job_update = {"state": "UploadComplete"}
    response = requests.patch(url, headers=headers, json=job_update)
    print(response)
    
    if response.status_code == 200:
        return jsonify({"message":"Job closed successfully."})
    else:
        return jsonify({"error":"Error while closing Job"})
    


if __name__ == '__main__':
    app.run(debug=True)
    

    





