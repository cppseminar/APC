import logging
import os
import time
import math

logger = logging.getLogger(__name__)

class TimeoutManager:
    # we will keep 15s for mantainance in this python app, it should be very 
    # generous and should be enough for everyone
    TIMEOUT = max(int(os.getenv('TIMEOUT', '500')) - 15, 0)

    def __init__(self):
        logger.debug('Current remaining timeout is %ds', self.__class__.TIMEOUT)

    def __enter__(self):
        self.start = time.perf_counter()
        return self.__class__.TIMEOUT

    def __exit__(self, type, value, traceback):
        del type, value, traceback # unused
        elapsed = math.ceil(time.perf_counter() - self.start)
        self.__class__.TIMEOUT = max(0, self.__class__.TIMEOUT - elapsed)
