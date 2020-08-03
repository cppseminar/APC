import datetime
import itertools
import json
import logging
import urllib

import azure.functions as func


def request_to_json(request: func.HttpRequest) -> dict:
    return {
        "route_params": dict(request.route_params),
        "url": request.url,
        "method": request.method,
        "headers": dict(request.headers),
        "params": dict(request.params),
        "form": request.form,
        "files": request.files,
        "body": request.get_body().decode("utf-8"),
    }

def dict_response(response: dict, code=200):
    return func.HttpResponse(
        json.dumps(response), status_code=code, mimetype="application/json"
    )


def mock_post_response(url):
    return {
        "link": url
    }

ENTRY1 = {
    "id" : 5,
    "user" : 22,
    "date": datetime.datetime(2020, 8, 22, 15, 14, 57, 110).isoformat(),
    "data" : "#include <stdio.h>\nint main() {}"
}

ENTRY2 = {
    "id" : 6,
    "user" : 234,
    "date": datetime.datetime(2010, 8, 22, 15, 14, 57, 110).isoformat(),
    "data" : "#include <stdlib.h>\nint main() {\n\treturn 1;\n}"
}



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    if req.method == "GET" and req.route_params.get("id", "") == "5":
        return dict_response(ENTRY1)

    if req.method == "GET" and req.route_params.get("id", "") == "6":
        return dict_response(ENTRY2)

    if req.method == "GET" and not req.route_params:
        return dict_response([ENTRY1, ENTRY2])

    if req.method == "POST":
        parsed = urllib.parse.urlparse(req.url)
        url = urllib.parse.urlunparse([*itertools.islice(parsed, 2), "api/submissions/6", None, None, None])
        return dict_response(mock_post_response(url), code=201)


    return dict_response(request_to_json(req), code=404)
