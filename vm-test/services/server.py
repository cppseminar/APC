from flask import Flask, request
from huey import FileHuey
from waitress import serve

import json
import tempfile

huey_dir = tempfile.mkdtemp(suffix='huey')

huey = FileHuey(path=huey_dir, levels=4, use_thread_lock=True)

app = Flask(__name__)

@huey.task()
def process_results(data):
    import time
    time.sleep(5)
    print(json.loads(data))

@app.route('/results', methods=['PATCH'])
def results():
    process_results(request.data)

    print("<p>Hello, World!</p>")
    return '', 200

def run():
    serve(app, host='0.0.0.0', port=10010)