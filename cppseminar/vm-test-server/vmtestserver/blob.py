import urllib.request
import os
import datetime

from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient, generate_blob_sas

class AzureFileError(RuntimeError):
    pass

def download_file(url):
    with urllib.request.urlopen(url) as response:
        if response.status >= 200 and response.status < 300:
            return response.read().decode('utf-8')

        raise AzureFileError('Cannot download file {}, ended with status {}.'.format(url, response.status))


def upload_file_and_get_token(filepath, container, conn_str):
    service = BlobServiceClient.from_connection_string(conn_str)

    container_client = service.create_container(container)

    blob_client = container_client.get_blob_client(os.path.basename(filepath))

    with open(filepath, 'rb') as f:
        blob_client.upload_blob(f, timeout=300)

        uri = urlparse(blob_client.url)
        blob_client_url = uri.scheme + '://' + uri.netloc + uri.path

        return blob_client_url + "?" + generate_blob_sas(
            blob_client.account_name,
            blob_client.container_name,
            blob_client.blob_name,
            account_key=service.credential.account_key,
            permission='r',
            expiry=datetime.datetime.now() + datetime.timedelta(days=5),
        )
