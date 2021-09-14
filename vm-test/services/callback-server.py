from flask import Flask, request
from waitress import serve
from azure.storage.blob import BlobServiceClient, generate_blob_sas
import pika

import tempfile
import json
import base64
import os
import uuid
import contextlib
import datetime
import logging
import sys
import signal


logger = logging.getLogger(__name__)

app = Flask(__name__)

TEMP_DIR = tempfile.mkdtemp(prefix='upload')


def set_up_logging():
    # setup logging on stdout
    logger = logging.getLogger('')
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))


def process_results(data):
    data = json.loads(data)

    result_zip = base64.b64decode(data['data'])
    zip_file_path = os.path.join(TEMP_DIR, str(uuid.uuid4())) + '.zip'
    try:

        with open(zip_file_path, 'wb') as f:
            f.write(result_zip)

        service = BlobServiceClient.from_connection_string(conn_str=os.getenv('RESULTS_BLOB_CONN_STR'))

        blob_client = service.get_blob_client(container='results', blob=os.path.basename(zip_file_path))

        with open(zip_file_path, 'rb') as f:
            blob = blob_client.upload_blob(f, timeout=300)

            token = generate_blob_sas(
                blob.account_name,
                blob.container_name,
                blob.blob_name,
                account_key=service.credential.account_key,
                permission='r',
                expiry=datetime.datetime.now() + datetime.timedelta(hours=1),
            )

            req = {
                'students': data['students'],
                'teachers': data['teachers'],
                'files': token,
            }

            with contextlib.closing(pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))) as connection:
                channel = connection.channel()

                channel.queue_declare(queue=os.getenv('RESULTS_QUEUE_NAME'), durable=True)

                channel.basic_publish(exchange='', routing_key=os.getenv('RESULTS_QUEUE_NAME'), body=json.dumps(req))

    finally:         
        with contextlib.suppress(FileNotFoundError):
            os.remove(zip_file_path)


@app.route('/results', methods=['POST'])
def results():
    process_results(request.data)
    return '', 200


@app.route('/', methods=['GET'])
def xxx():
    import time
    time.sleep(15)
    process_results(request.data)
    return '', 200


def signal_term_handler(signal, _):
    logger.debug('Received %d', signal)
    raise KeyboardInterrupt()


if __name__ == '__main__':
    set_up_logging()

    try:
        logger.info('Starting...')
        
        logger.debug('Setting up SIGTERM handler')
        signal.signal(signal.SIGTERM, signal_term_handler)

        serve(app, host='0.0.0.0', port=int(os.getenv('RETURN_PORT')))

        logger.info('Finished.')
    except KeyboardInterrupt:
        logger.info('Interrupted.')