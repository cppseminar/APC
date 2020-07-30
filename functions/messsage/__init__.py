import json
import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    response = {"message" : "Hello from azure functions!"}
    return func.HttpResponse(
             json.dumps(response),
             status_code=200,
             mimetype="application/json"
        )
