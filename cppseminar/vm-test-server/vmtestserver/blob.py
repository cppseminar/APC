import http.client
import os
import datetime

from azure.storage.blob import BlobServiceClient, generate_blob_sas
from urllib.parse import urlparse

class AzureFileError(RuntimeError):
    pass

def download_file(url):
    uri = urlparse(url)

    connection = http.client.HTTPConnection(uri.netloc, timeout=60)
    try:
        connection.request('GET', uri.path + '?' + uri.query)
        response = connection.getresponse()
        if response.status >= 200 and response.status < 300:
            return response.read().decode('utf-8')

        raise AzureFileError('Cannot download file {}, ended with status {}.'.format(url, response.status))
    finally:
        connection.close()


def upload_file_and_get_token(filepath, container, conn_str):
    service = BlobServiceClient.from_connection_string(conn_str)

    blob_client = service.get_blob_client(container=container, blob=os.path.basename(filepath))

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
