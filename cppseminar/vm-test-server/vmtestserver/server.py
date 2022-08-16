from flask import Flask, request

from .requests import process_results

app = Flask(__name__)

@app.route('/results', methods=['POST'])
def results():
    process_results(request.data)
    return '', 200
