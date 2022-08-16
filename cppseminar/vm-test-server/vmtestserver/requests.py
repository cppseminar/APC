from http import HTTPStatus
import json
import os
import logging
import http.client
import base64
import tempfile
import uuid
import contextlib
import pika

from .blob import upload_file_and_get_token, AzureFileError

TEMP_DIR = tempfile.mkdtemp(prefix='upload')

logger = logging.getLogger(__name__)

def process_results(data):
    data = json.loads(data)

    result_zip = base64.b64decode(data['data'])
    zip_file_path = os.path.join(TEMP_DIR, str(uuid.uuid4())) + '.zip'
    students_file_path = os.path.join(TEMP_DIR, str(uuid.uuid4())) + '.zip'
    teachers_file_path = os.path.join(TEMP_DIR, str(uuid.uuid4())) + '.zip'
    try:
        with open(zip_file_path, 'wb') as f:
            f.write(result_zip)

        with open(students_file_path, 'w') as f:
            json.dump(data['students'], f)

        with open(teachers_file_path, 'w') as f:
            json.dump(data['teachers'], f)

        connection_string = os.getenv('RESULTS_BLOB_CONN_STR')

        req = {
            'students': upload_file_and_get_token(students_file_path, 'vm-test-students', connection_string),
            'teachers': upload_file_and_get_token(teachers_file_path, 'vm-test-teachers', connection_string),
            'data': upload_file_and_get_token(zip_file_path, 'vm-test-results', connection_string),
            'metaData': data['metaData'], # forward metadata
        }

        with contextlib.closing(pika.BlockingConnection(
            pika.ConnectionParameters(host=os.getenv('RABBIT_MQ')))) as connection:
            channel = connection.channel()

            # No queue declare here, we expect that queue will be declared by tester service.
            channel.basic_publish(exchange='', routing_key=os.getenv('RESULTS_QUEUE_NAME'), body=json.dumps(req))

    except Exception as e:
        logger.error("Encountered exception while processing results.", exc_info=e)
        raise
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.remove(zip_file_path)
            os.remove(students_file_path)
            os.remove(teachers_file_path)

