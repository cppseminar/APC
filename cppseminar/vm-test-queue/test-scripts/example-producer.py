import pika
import os
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(os.getenv('RABBIT_MQ')))
channel = connection.channel()

channel.queue_declare(queue=os.getenv('SUBMISSION_QUEUE_NAME'), durable=True)

req = {
    'dockerImage': 'example',
    'submittedFiles': {
        'main.cpp': 'http://azurite.local:10000/azuriteuser/submissions/foldrik/submission.cpp?sv=2018-03-28&st=2021-09-17T15%3A40%3A09Z&se=2021-09-18T15%3A40%3A09Z&sr=b&sp=r&sig=Mka9TL5oRPk1s1HqnBDEcR0zq82%2FCMWL6EiN4mq6my8%3D'
    }
}

channel.basic_publish(exchange='', routing_key=os.getenv('SUBMISSION_QUEUE_NAME'), body=json.dumps(req))
connection.close()