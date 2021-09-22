import sys
import logging.config
import logging
import os
import json

from tester.config import Config

def configure():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname:8s} {asctime} {module:14s} {funcName:15s} {message}',
                'style': '{',
            }
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(Config.output_path(), 'main-tester.log'),
                'mode': 'w',
                'formatter': 'verbose',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'root': {
            'level': 'NOTSET',
            'handlers': ['console', 'file']
        },
    })

logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    try:
        logger.exception('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))
        logger.debug('Creating json with errors')

        output = {
            'status': 'Exception',
            'text': 'This should never happen, please report this incident to your friendly administrators.',
        }

        with open(Config.teachers_json(), 'w') as f:
            json.dump(output, f)

        with open(Config.students_json(), 'w') as f:
            json.dump(output, f)
    finally:
        sys.exit(0)

sys.excepthook = handle_exception
