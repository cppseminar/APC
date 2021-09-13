import sys
import os
import pika
import threading

from services.queue import run as qrun
from services.server import run as srun

import logging

import azure.storage.blob
from azure.storage.blob import BlobServiceClient
# Acquire the logger for a library (azure.mgmt.resource in this example)
logger = logging.getLogger('azure')

# Set the desired logging level
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

def run():

    service = BlobServiceClient.from_connection_string(conn_str="DefaultEndpointsProtocol=http;AccountName=azuriteuser;AccountKey=UGFzc3dvcmQxMjMhfg==;BlobEndpoint=http://azurite.local:10000/azuriteuser;", logging_enable=True)

    container_client = service.get_container_client('results')
    container_client.create_container()


    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    try:
        threads = [
            threading.Thread(target=qrun, args=(channel,)),
            threading.Thread(target=srun)
        ]
        
        for i in threads:
            i.start()

        for x in threads:
            x.join()
    finally:
        connection.close()

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)