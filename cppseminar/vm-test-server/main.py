from waitress import serve

import os
import logging
import sys
import signal

from vmtestserver.server import app

logger = logging.getLogger(__name__)



def set_up_logging():
    # setup logging on stdout
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    logger = logging.getLogger('azure')
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

        serve(app, port=os.getenv('HTTP_LISTEN_PORT'))

        logger.info('Finished.')
    except KeyboardInterrupt:
        logger.info('Interrupted.')
