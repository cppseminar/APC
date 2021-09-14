import json
import os
import socket
import logging
import http.client
import sys
import pika
import signal

from contextlib import closing
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


STOP = False


def set_up_logging():
    # setup logging on stdout
    logger = logging.getLogger('')
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))


def send_request_to_vm(data):
    connection = http.client.HTTPConnection('localhost:10009', timeout=60)
    try:
        connection.request('POST', '/test', json.dumps(data))
        response = connection.getresponse()
        return response.status >= 200 and response.status < 300
    finally:
        connection.close()


def download_file(url):
    uri = urlparse(url)

    connection = http.client.HTTPConnection(uri.netloc, timeout=60)
    try:
        connection.request('GET', uri.path + '?' + uri.query)
        response = connection.getresponse()
        if response.status >= 200 and response.status < 300:
            return response.read().decode('utf-8')

        raise RuntimeError('Cannot download file %s, ended with status %d.', url, response.status)
    finally:
        connection.close()


def process(ch, method, body, return_port):
    try:
        req = json.loads(body)

        meta_data = req.get('metaData', {})

        # docker container url will go here
        docker_image = req['dockerImage']

        # timeout and memory for the test run
        max_run_time = req.get('maxRunTime', None)
        memory = req.get('memory', None)

        # path to submitted file, we should load this from blob storage
        # currently the file is here
        submitted_files = req['submittedFiles']
        for k, v in submitted_files.items():
            submitted_files[k] = download_file(v)

        vm_request = {
            'returnUrl': socket.gethostname() + ':' + str(return_port),
            'metaData': meta_data,
            'dockerImage': docker_image,
            'files': submitted_files,
        }
        import time
        time.sleep(15)
        if max_run_time:
            vm_request['maxRunTime'] = max_run_time
        if memory:
            vm_request['memory'] =  memory

        send_request_to_vm(vm_request)
    except Exception as e:
        logger.warn("Encountered exception on message %s", body, exc_info=e)
    finally:
        # on failure we may want to requeue the message or something
        ch.basic_ack(delivery_tag = method.delivery_tag)


def run():
    with closing(pika.BlockingConnection(pika.ConnectionParameters('localhost'))) as connection:
        channel = connection.channel()

        queue_name = os.getenv('SUBMISSION_QUEUE_NAME')
        return_port = os.getenv('RETURN_PORT')

        channel.queue_declare(queue_name, durable=True)

        for msg in channel.consume(queue_name, inactivity_timeout=2):
            if STOP:
                logger.info('Breaking from msg loop.')
                break

            if msg == (None, None, None):
                continue

            method, _, body = msg
            process(channel, method, body, return_port)


def signal_term_handler(signal, _):
    logger.warning('Received %d', signal)
    global STOP 
    STOP= True


if __name__ == '__main__':
    set_up_logging()

    try:
        logger.info('Starting...')
        
        logger.debug('Setting up SIGTERM handler')
        signal.signal(signal.SIGTERM, signal_term_handler)
        signal.signal(signal.SIGINT, signal_term_handler)

        run()

        logger.info('Finished.')

    except Exception as e:
        logger.critical('Exception occured!', exc_info=e)
