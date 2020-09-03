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
from ..shared import http, decorators, mongo, users


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Entry point."""
    dispatch = shared.http.dispatcher(get=get_handler, post=post_handler)
    return dispatch(req)


@shared.decorators.login_required
@shared.decorators.validate_parameters(
    route_settings=ROUTE_PARAMS, query_settings=QUERY_PARAMS
)
def get_handler(
    req: func.HttpRequest,
    user: shared.users.User,
    submission_id=None,
    skip=0,
    limit=10,
    user_filter=None,
    task_id=None,
):
    """Handle list requests and concrete id request."""

    # We want one concrete reponse
    if submission_id:
        result = mongo.MongoSubmissions.get_submission(submission_id=submission_id)
        if not result:
            return http.response_not_found()

        if not user.is_admin and user.email != result.user:
            return http.response_forbidden()
        return http.response_ok(result)
    # We are listing all
    if not user.is_admin:
        if user_filter != user.email:
            return http.response_forbidden()

    submissions = mongo.MongoSubmissions.get_submissions(
        skip=skip, limit=limit, user=user_filter, task_id=task_id
    )
    return http.response_ok(list(submissions))


@shared.decorators.login_required
def post_handler(req: func.HttpRequest, user=None):
    """Handle new submissions."""
    document = http.get_json(req, POST_SCHEMA)
    # TODO: Tasks must have time interval for submissions
    if not document:
        return http.response_client_error()
    # Let's check if user has right to submit to this task
    roles = None
    if not user.is_admin:
        roles = user.roles or []
    result = mongo.MongoTasks.get_task(ObjectId(document["taskId"]), roles=roles)
    if not result:
        return http.response_client_error()
    # User has right to do this
    result = mongo.MongoSubmissions.submit(
        user=user.email, files=document["files"], task_id=ObjectId(document["taskId"])
    )

    return http.response_ok(result, code=201)
