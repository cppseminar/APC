import pika, json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='test-vm', durable=True)

req = {
    'returnUrl': 'localhost:10010',
    'test': 'tmp',
    'submittedFiles': {
        'main.cpp': 'Cannot compile'
    }
}

channel.basic_publish(exchange='', routing_key='test-vm', body=json.dumps(req))
connection.close()