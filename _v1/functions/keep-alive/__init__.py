import logging

import azure.functions as func


from ..shared import http


def main(req: func.HttpRequest) -> func.HttpResponse:
    response = {
        "message": "ok"
    }
    return http.response_ok(response)
