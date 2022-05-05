
"""
File implementing all functions for listing backups.
"""
import logging

from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)


def list_backups(azure_container, azure_connection):
    """
    List all backup files from azure storage blob container.
    """
    logger.info('Listing all backups started.')

    service = BlobServiceClient.from_connection_string(azure_connection)

    container_client = service.get_container_client(azure_container)

    blob_list = container_client.list_blobs(timeout=15)

    print('Found entries:')
    for blob in blob_list:
        print('\t' + blob.name)
