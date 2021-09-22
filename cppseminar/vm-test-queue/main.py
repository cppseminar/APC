import os
import logging
import http.client
import sys
import pika
import signal
import socket

from contextlib import closing
from threading import Event

logger = logging.getLogger(__name__)


stop = Event()


def set_up_logging():
    # setup logging on stdout
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    logger = logging.getLogger('pika')
    # it will polute logs with useless stuff when the rabbit mq is not yet runnig
    # we will switch to warning, when either first connection is made or 
    # sufficient time has elapased
    logger.setLevel(logging.CRITICAL)


def forward_request_to_vm_test_server(channel, method, data):
    server_addr = os.getenv('VM_TEST_SERVER')

    try:
        connection = http.client.HTTPConnection(server_addr, timeout=60)
        connection.request('POST', '/test', data)
        response = connection.getresponse()
        if response.status >= 200 and response.status < 300:
            channel.basic_ack(delivery_tag = method.delivery_tag)
            return True
        else:
            logger.warning('Http request POST /test on %s failed with %d %s', server_addr, response.status, response.reason)
            return False
    except Exception as e:
        logger.exception('Exception occurred request POST /test on %s.', server_addr, exc_info=e)
        return False
    finally:
        connection.close()


def connect():
    with closing(pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBIT_MQ')))) as connection:
        logging.getLogger('pika').setLevel(logging.WARNING) # we made connection, hooray!
        
        channel = connection.channel()

        queue_name = os.getenv('SUBMISSION_QUEUE_NAME')
        channel.queue_declare(queue_name, durable=True)

        for msg in channel.consume(queue_name, inactivity_timeout=2):
            if stop.is_set():
                logger.info('Breaking from msg loop.')
                break

            if msg == (None, None, None):
                continue

            method, _, body = msg
            if not forward_request_to_vm_test_server(channel, method, body):
                logger.warning('Cannot forward message %s', body.decode('utf8'))


def run():
    tries = 0
    total_waittime = 0

    while True:
        try:
            if total_waittime >= 30:
                # if we cannot start in more than 30s, there is something seriosly wrong with us, so log it
                logging.getLogger('pika').setLevel(logging.WARNING)

            connect()
            break
        except (pika.exceptions.AMQPConnectionError, socket.gaierror):
            waittime = min(tries // 2, 15)
            
            logger.warning('Cannot connect to rabbit mq server, wait %ds', waittime)
            if stop.wait(timeout=waittime):
                logger.warning('Connection is not possible, but we must stop.')
            
            total_waittime += waittime
            tries += 1
            continue

def signal_handler(signal, _):
    logger.warning('Received %d', signal)
    stop.set()
    logger.info('Stopping...')


if __name__ == '__main__':
    set_up_logging()

    try:
        logger.info('Starting...')
        
        logger.debug('Setting up signals handlers')
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        run()

        logger.info('Finished.')

    except Exception as e:
        logger.critical('Exception occured!', exc_info=e)
