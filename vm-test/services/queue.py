import json
import socket
import http.client

def send_request_to_vm(data):
    try:
        connection = http.client.HTTPConnection('localhost:10009', timeout=60)
        connection.request('POST', '/test', json.dumps(data))
        response = connection.getresponse()
        return response.status >= 200 and response.status < 300
    except Exception as e:
        return False


def donwload_file(url):
    try:
        connection = http.client.HTTPConnection(url, timeout=60)
        connection.request('GET')
        response = connection.getresponse()
        return response.status >= 200 and response.status < 300
    except Exception as e:
        return None


def process(ch, method, body):
    req = json.loads(body)

    meta = req.get('meta', {})

    # docker container url will go here
    test = req['test']

    # timeout and memory for the test run
    timeout = req.get('timeout', None)
    memory = req.get('memory', None)

    # path to submitted file, we should load this from blob storage
    # currently the file is here
    submitted_files = req['submittedFiles']

    vm_request = {
        'returnUrl': socket.gethostname() + ':10010',
        'meta': meta,
        'dockerImage': test,
        'files': submitted_files,
    }

    if timeout:
        vm_request['maxRunTime'] = timeout
    if memory:
        vm_request['memory'] =  memory

    send_request_to_vm(vm_request)
    # on failure we may want to requeue the message or something
    ch.basic_ack(delivery_tag = method.delivery_tag)

def run(channel):
    channel.queue_declare('test-vm', durable=True)

    callback = lambda ch, method, _, body: process(ch, method, body)
    channel.basic_consume(queue='test-vm', on_message_callback=callback)

    channel.start_consuming()