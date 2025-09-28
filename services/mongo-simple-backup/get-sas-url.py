from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta, UTC

import sys
import os
from urllib.parse import urlparse

def container_exists(blob_service_client, container_name):
    """Check if a container exists in Azure Blob Storage."""
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.get_container_properties()
        return True
    except Exception:
        return False

def generate_sas_url(connection_string, container_name, file_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Check if container exists, create it if it doesn't
    if not container_exists(blob_service_client, container_name):
        print(f"Container '{container_name}' does not exist. Creating it...")
        container_client = blob_service_client.create_container(container_name)

    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=file_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(write=True),
        expiry=datetime.now(UTC) + timedelta(hours=1)  # SAS token valid for 1 hour
    )

    sas_url = f"{blob_service_client.url}{container_name}/{file_name}?{sas_token}"

    return sas_url

if __name__ == "__main__":
    connection_string = os.getenv("DUMPS_BLOB_CONN_STR", None)
    if connection_string is None:
        print("Error: DUMPS_BLOB_CONN_STR environment variable is not set")
        sys.exit(1)

    if len(sys.argv) != 3:
        print("Usage: python get-sas-url.py <container_name> <file_name>")
        sys.exit(1)

    container_name = sys.argv[1]
    file_name = sys.argv[2]

    try:
        sas_url = generate_sas_url(connection_string, container_name, file_name)
        print(sas_url)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
