"""Validation functions for tests endpoint."""

from ..shared import decorators, core

SCHEMA_SUBMISSION_ID = "submissionId"
SCHEMA_CASE_ID = "testCaseId"

POST_SCHEMA = {
    SCHEMA_SUBMISSION_ID : {
        "type": "string",
        "required": True,
        "empty": False,
        "check_with": core.cerberus_object_id_validator,
    },
    SCHEMA_CASE_ID : {
        "type": "string",
        "required": True,
        "empty": False,
        "check_with": core.cerberus_object_id_validator,
    },
}


ROUTE_SETTINGS = {
    "id": {decorators.VALIDATOR: decorators.object_id_validator,
    decorators.DESTINATION: "test_id"}
}
