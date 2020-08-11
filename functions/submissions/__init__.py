"""This is implementation of submissions.

We support:
- GET on all submissons (you can specify offset as parameter)
- GET on specific objectID
- POST to post new data
"""
import contextlib
import datetime
import itertools
import json
import logging
import os
import urllib
import typing

import azure.functions as func
import cerberus

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS


from .validators import POST_SCHEMA, QUERY_PARAMS, ROUTE_PARAMS

from .. import shared
from ..shared import http, decorators, mongo


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Entry point."""
    dispatch = shared.http.dispatcher(get=get_handler, post=post_handler)
    return dispatch(req)



@shared.decorators.login_required
@shared.decorators.validate_parameters(
    route_settings=ROUTE_PARAMS, query_settings=QUERY_PARAMS
)
def get_handler(req: func.HttpRequest, submission_id=None, skip=0, limit=10):
    """Handle list requests and concrete id request."""

    if submission_id:
        result = mongo.MongoSubmissions.get_submission(submission_id=submission_id)
        if not result:
            return http.response_not_found()
        return http.response_ok(result)

    submissions = mongo.MongoSubmissions.get_submissions(skip=skip, limit=limit)
    return http.response_ok(list(submissions))


@shared.decorators.login_required
def post_handler(req: func.HttpRequest):
    """Handle new submissions."""

    client = MongoClient(os.environ["MyCosmosDBConnectionString"], retryWrites=False)
    db = client.get_database("development")
    collection = db.get_collection("submissions")

    # Someone is adding new value
    submit = None
    try:
        request_json = req.get_json()
        request_json = dict(request_json)
        global POST_SCHEMA
        validator = cerberus.Validator(POST_SCHEMA)
        if not validator.validate(request_json):
            logging.info("Error in submission post %s", validator.errors)
            raise RuntimeError("Bad json schema")

        if "_id" in request_json:
            raise RuntimeError("Trying to set _id")
        # For now, this is fine
        submit = request_json
    except Exception:
        return http.response_client_error()

    result = collection.insert_one(submit)
    new_id = str(result.inserted_id)

    parsed = urllib.parse.urlparse(req.url)
    editable = list(parsed)

    # Fix slash on the end of uri
    uri = editable[2]
    slash = ""
    if uri and uri[-1] != "/":
        slash = "/"
    editable[2] = str(uri) + slash + f"{new_id}"
    # Done

    url = urllib.parse.urlunparse(editable)

    return http.response_ok({"link": url})
