from flask import Flask, request
from waitress import serve
from azure.storage.blob import BlobServiceClient

import tempfile
import json
import base64
import os
import uuid
import contextlib

app = Flask(__name__)

TEMP_DIR = tempfile.mkdtemp(prefix='upload')

def process_results(data):
    data = json.loads(data)

    result_zip = base64.decodebytes(data['result'].encode('utf8'))
    zip_file_path = os.path.join(TEMP_DIR, str(uuid.uuid4())) + '.zip'
    try:

        with open(zip_file_path, 'wb') as f:
            f.write(result_zip)

        service = BlobServiceClient.from_connection_string(conn_str="DefaultEndpointsProtocol=http;AccountName=azuriteuser;AccountKey=UGFzc3dvcmQxMjMhfg==;BlobEndpoint=http://azurite.local:10000/azuriteuser;")

        container_client = service.get_container_client('results')
        container_client.create_container()

        blob_client = service.get_blob_client(container='results', blob=zip_file_path)

        with open(zip_file_path, 'rb') as f:
            blob_client.upload_blob(f, timeout=300)

    except:
        with contextlib.suppress(FileNotFoundError):
            os.remove(zip_file_path)

        raise

@app.route('/results', methods=['PATCH'])
def results():
    process_results(request.data)
    return '', 200

def run():
    serve(app, host='0.0.0.0', port=10010)