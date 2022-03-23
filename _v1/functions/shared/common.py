import os
import json
from types import SimpleNamespace

from bson import ObjectId

# Http headers set by gateway (either azure api management) or some web server
HTTP_HEADER_HOST     = "X-FORWARDED-HOST"
HTTP_HEADER_PORT     = "X-FORWARDED-PORT"
HTTP_HEADER_PROTOCOL = "X-FORWARDED-PROTO"
HTTP_HEADER_EMAIL    = "X-REQUEST-EMAIL"
##############################################################################

# All required or optional environment variables
ENV_STORAGE_STRING    = "AzureWebJobsStorage"
ENV_CONNECTION_STRING = "MyCosmosDBConnectionString"
ENV_HOST_OVERRIDE     = "DEBUG_HOST_OVERRIDE"  # Optional
ENV_DB_NAME           = "COSMOS_DB"  # Optional
ENV_QUEUE_NAME        = "QUEUE_NAME"
ENV_QUEUE_SECRET      = "QUEUE_SECRET"
################################################

# Azure table keywords for testers
TABLE_VM_NAME = "testers"

TESTER_PARTITION_KEY = "PartitionKey"
TESTER_ROW_KEY       = "RowKey"
TESTER_START_URL     = "startURL" # Optional: Required by stopAfter
TESTER_STOP_URL      = "stopURL" # Optional: Required by stopAfter
TESTER_URL           = "url"
TESTER_SECRET        = "secret"
TESTER_STOP_AFTER    = "stopAfter" # Optional: Number of seconds to keep alive
##################################

DB_NAME =  os.getenv(ENV_DB_NAME) or "development"  # Mongo db name
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
