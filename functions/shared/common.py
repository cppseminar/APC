import os
import json
from types import SimpleNamespace

from bson import ObjectId

HTTP_HEADER_HOST = "X-FORWARDED-HOST"
HTTP_HEADER_PORT = "X-FORWARDED-PORT"
HTTP_HEADER_PROTOCOL = "X-FORWARDED-PROTO"

ENV_CONNECTION_STRING = "MyCosmosDBConnectionString"
ENV_QUEUE_URL = "QUEUE_URL"
ENV_QUEUE_SECRET = "QUEUE_SECRET"
ENV_HOST_OVERRIDE = "DEBUG_HOST_OVERRIDE"
ENV_DB_NAME = "COSMOS_DB"
ENV_QUEUE_NAME = "QUEUE_NAME"

HEADER_EMAIL = "X-REQUEST-EMAIL"
DB_NAME =  os.getenv(ENV_DB_NAME) or "development"
COL_USERS = "users"
COL_SUBMISSIONS = "submissions"
COL_TASKS = "tasks"
COL_CASES = "test_cases"
COL_TESTS = "submitted_tests"

SCHEMA_USER = SimpleNamespace(EMAIL="email", ROLES="roles", IS_ADMIN="is_admin",)

SCHEMA_TASKS_NAME = "name"
SCHEMA_TASKS_DESCRIPTION = "description"


# tests collection
COL_TESTS_USER = "user"
COL_TESTS_REQUESTED = "requested"

def encode_message(url: str, case_id: ObjectId, submission_id: ObjectId):
    """Encodes parameters to string, so it may be processed by azure queue."""
    return json.dumps(
        {
            "url": url,
            "caseId": str(case_id),
            "submissionId": str(submission_id),
        },
        indent=2,
    )

def decode_message(message: str):
    """Decodes messages encoded by encode message."""
    result = json.loads(message)
    return (
        result["url"],
        ObjectId(result["caseId"]),
        ObjectId(result["submissionId"])
        )
