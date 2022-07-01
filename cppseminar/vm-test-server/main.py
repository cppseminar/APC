from waitress import serve

import logging
import sys
import signal
import json
import os

from vmtestserver.server import app

logger = logging.getLogger(__name__)

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
            message['level'] = 'Error'
        elif record.levelname in ['WARN', 'NOTSET']: # not sure if NOTSET can happen
            message['level'] = 'Warning'
        elif record.levelname in ['INFO']:
            pass # keep empty
        else:
            message['level'] = 'Verbose'

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

    logger = logging.getLogger('azure')
    logger.setLevel(logging.WARNING)

    logger = logging.getLogger('pika')
    logger.setLevel(logging.WARNING)

def signal_term_handler(signum, _):
    logger.info('Received signal %d', signum)
    raise KeyboardInterrupt() # this will stop waitress from serving


if __name__ == '__main__':
    set_up_logging()

    try:
        logger.info('Starting...')

        logger.debug('Setting up SIGTERM handler')
        signal.signal(signal.SIGTERM, signal_term_handler)

        serve(app, port=80)

        logger.info('Finished.')
    except KeyboardInterrupt:
        logger.info('Interrupted.')
