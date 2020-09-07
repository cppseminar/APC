"""Validation functions for tests endpoint."""

from ..shared import decorators, core

SCHEMA_SUBMISSION_ID = "submissionId"
SCHEMA_CASE_ID = "testCaseId"

POST_SCHEMA = {
    SCHEMA_SUBMISSION_ID: {
        "type": "string",
        "required": True,
        "empty": False,
        "check_with": core.cerberus_object_id_validator,
    },
    SCHEMA_CASE_ID: {
        "type": "string",
        "required": True,
        "empty": False,
        "check_with": core.cerberus_object_id_validator,
    },
}

def _email_validator(email):
    if core.is_email(email):
        return str(email)
    raise RuntimeError(f"Invalid email in query params {email}")

ROUTE_SETTINGS = {
    "id": {
        decorators.VALIDATOR: decorators.object_id_validator,
        decorators.DESTINATION: "test_id",
    }
}

QUERY_SETTINGS = {
    "user": {
        decorators.VALIDATOR: _email_validator,
        decorators.DESTINATION: "email",
    },
    "submission": {
        decorators.VALIDATOR: decorators.object_id_validator,
        decorators.DESTINATION: "submission_id",
    },
    "task": {
        decorators.VALIDATOR: decorators.object_id_validator,
        decorators.DESTINATION: "task_id",
    }

}

