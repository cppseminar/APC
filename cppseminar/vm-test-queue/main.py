import os
import logging
import http.client
import sys
import pika
import signal
import socket
import json
import datetime

from contextlib import closing
from threading import Event

logger = logging.getLogger(__name__)

stop = Event()

class JsonFormatter(logging.Formatter):
    def format(self, record):
        """Formats a log record and serializes to json. Which out logstash 
        will understand. """
        message = {}
        message['@m'] = record.getMessage()
        if record.exc_info:
            message['@m'] += ' EXC_INFO: ' + self.formatException(record.exc_info)

        if record.exc_text:
            message['@m'] += ' EXC_TEXT: ' + record.exc_text

        if record.stack_info:
            message['@m'] += ' STACK_INFO: ' + self.formatStack(record.stack_info)

        if record.levelname in ['CRITICAL', 'ERROR']:
            message['@l'] = 'Error'
        elif record.levelname in ['WARN', 'NOTSET']: # not sure if NOTSET can happen
            message['@l'] = 'Warning'
        elif record.levelname in ['INFO']:
            pass # keep empty
        else:
            message['@l'] = 'Verbose'

        return json.dumps(message)


def set_up_logging():
    # setup logging on stdout
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)

    logHandler = logging.StreamHandler(stream=sys.stdout)
    # if LOG_PRETTY is set to '1' do not log as json
    if os.getenv('LOG_PRETTY', '0') != '1':
        formatter = JsonFormatter()
        logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    pika_logger = logging.getLogger('pika')
    # it will polute logs with useless stuff when the rabbit mq is not yet runnig
    # we will switch to warning, when either first connection is made or
    # sufficient time has elapased
    pika_logger.setLevel(logging.CRITICAL)


def forward_request_to_vm_test_server(channel, method, data):
    server_addr = os.getenv('VM_TEST_SERVER')

    try:
        connection = http.client.HTTPConnection(server_addr, timeout=60)
        connection.request('POST', '/test', data)
        response = connection.getresponse()
        if response.status >= 200 and response.status < 300:
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
    logger.info('Try to connect to Rabbit MQ %s.', os.getenv('RABBIT_MQ'))

    with closing(pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBIT_MQ')))) as connection:
        logger.info('Connected to Rabbit MQ.')
        
        logging.getLogger('pika').setLevel(logging.WARNING) # we made connection, hooray!

        channel = connection.channel()

        queue_name = os.getenv('SUBMISSION_QUEUE_NAME')
        # We are not going to declare queue here to avoid duplication.
        # Queue will be declared by test service
        # channel.queue_declare(queue_name, durable=True)

        # we set auto ack to True, if we cannot forward the message we 
        # si,ply discard it, it is not ideal, but for now better, than
        # fail in a loop
        for msg in channel.consume(queue_name, auto_ack=True, inactivity_timeout=2):
            if stop.is_set():
                logger.info('Breaking from msg loop.')
                break

            if msg == (None, None, None):
                continue

            method, _, body = msg
            if not forward_request_to_vm_test_server(channel, method, body):
                logger.warning('Cannot forward message %s', body.decode('utf8'))



def run():
    start = datetime.datetime.now()

    while True:
        try:
            total_waittime = (datetime.datetime.now() - start).total_seconds()

            if total_waittime >= 15:
                # if we cannot start in more than 15s, there is something seriosly wrong with us, so try to log it
                logging.getLogger('pika').setLevel(logging.INFO)
            if total_waittime >= 30:
                return False

            connect()

            return True
        except (pika.exceptions.AMQPConnectionError, socket.gaierror, pika.exceptions.ChannelClosedByBroker) as e:       
            logger.error('Communication error with queue', exc_info=e)

        except Exception as e:
            logger.error('Unhandled exception in message loop!', exc_info=e)
            return False

        logger.warning('Cannot connect to Rabbit MQ server queue, wait 1s.')
        if stop.wait(timeout=1):
            logger.warning('Connection is not possible, but we must stop.')
            return True

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

        if not run():
            logger.error('Encountered error.')
            sys.exit(1)
        
        logger.info('Finished.')

    except Exception as e:
        logger.critical('Exception occured!', exc_info=e)
        sys.exit(1)
