import json
import logging
import os

import azure.functions as func



def dump_dict(request: func.HttpRequest) -> dict:
    return {
        "route_params": dict(request.route_params),
        "url": request.url,
        "method": request.method,
        "headers": dict(request.headers),
        "params": dict(request.params),
        "form": request.form,
        "files": request.files,
        "body": request.get_body().decode("utf-8"),
        "environment": dict(os.environ)
    }



def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps(dump_dict(req)),
        mimetype="application/json"
    )
