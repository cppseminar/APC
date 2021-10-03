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

from .blob import download_file, upload_file_and_get_token, AzureFileError

TEMP_DIR = tempfile.mkdtemp(prefix='upload')

logger = logging.getLogger(__name__)

def process_results(data):
    data = json.loads(data)

    result_zip = base64.b64decode(data['data'])
    zip_file_path = os.path.join(TEMP_DIR, str(uuid.uuid4())) + '.zip'
    try:
        with open(zip_file_path, 'wb') as f:
            f.write(result_zip)

        token = upload_file_and_get_token(zip_file_path, 'results', os.getenv('RESULTS_BLOB_CONN_STR'))

        req = {
            'students': data['students'],
            'teachers': data['teachers'],
            'files': token,
            'metaData': data['metaData'], # forward metadata
        }

        with contextlib.closing(pika.BlockingConnection(
            pika.ConnectionParameters(host=os.getenv('RABBIT_MQ')))) as connection:
            channel = connection.channel()

            # No queue declare here, we expect that queue will be declared by
            # tester service.

            channel.basic_publish(exchange='', routing_key=os.getenv('RESULTS_QUEUE_NAME'), body=json.dumps(req))

    finally:
        with contextlib.suppress(FileNotFoundError):
            os.remove(zip_file_path)

def send_request_to_vm(data):
    vm_addr = os.getenv('VM_TEST_ADDR')

    try:
        connection = http.client.HTTPConnection(vm_addr, timeout=60)
        connection.request('POST', '/test', data)
        response = connection.getresponse()
        if response.status < 200 or response.status >= 300:
            logger.warning('Http request POST /test on %s failed with %d %s', vm_addr, response.status, response.reason)

        return response.status
    except ConnectionRefusedError:
        logger.info('Test VM (%s) seems to be not online.', vm_addr)
        return HTTPStatus.SERVICE_UNAVAILABLE
    except Exception as e:
        logger.exception('Exception occurred request POST /test on %s.', vm_addr, exc_info=e)
        return HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        connection.close()

def process_test(data):
    try:
        req = json.loads(data)

        meta_data = req.get('metaData', {})

        # docker container url will go here
        docker_image = req['dockerImage']

        # timeout and memory for the test run
        max_run_time = req.get('maxRunTime', None)
        memory = req.get('memory', None)

        # path to submitted file, we should load this from blob storage
        submitted_file = download_file(req['contentUrl'])

        vm_request = {
            'returnUrl': os.getenv('VM_TEST_RETURN_ADDR'),
            'metaData': meta_data,
            'dockerImage': docker_image,
            'files': {
                'main.cpp': submitted_file,
            },
        }

        if max_run_time:
            vm_request['maxRunTime'] = max_run_time
        if memory:
            vm_request['memory'] =  memory

        return send_request_to_vm(json.dumps(vm_request))
    except AzureFileError as e:
        logger.warn(e)
    except Exception as e:
        logger.warn("Encountered exception on message %s", data, exc_info=e)
        return HTTPStatus.INTERNAL_SERVER_ERROR
