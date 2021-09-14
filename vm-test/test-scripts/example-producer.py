import pika, json, os

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=os.getenv('SUBMISSION_QUEUE_NAME'), durable=True)

req = {
    'dockerImage': 'example',
    'submittedFiles': {
        'main.cpp': ''
    }
}

channel.basic_publish(exchange='', routing_key=os.getenv('SUBMISSION_QUEUE_NAME'), body=json.dumps(req))
connection.close()