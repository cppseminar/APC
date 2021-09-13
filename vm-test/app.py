import sys
import os
import pika
import threading

from services.queue import run as qrun
from services.server import run as srun

def run():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    try:
        threads = [
            threading.Thread(target=qrun, args=(channel,)),
            threading.Thread(target=srun)
        ]
        
        for i in threads:
            i.start()

        for x in threads:
            x.join()
    finally:
        connection.close()

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)