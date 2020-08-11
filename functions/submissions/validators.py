"""Validation config and functions for submissions."""
from ..shared import decorators

POST_SCHEMA = {
    "files": {
        "type": "list",
        "required": True,
        "items": [
            {
                "type": "dict",
                "require_all": True,
                "schema": {
                    "fileName": {"type": "string"},
                    "content": {"type": "string"},
                },
            }
        ],
    },
    "taskId": {"type": "string", "required": True, "empty": False},
}

ROUTE_PARAMS = {
    "id": {
        decorators.VALIDATOR: decorators.object_id_validator,
        decorators.DESTINATION: "submission_id",
    }
}


def _limit_validator(value):
    number = int(value)
    if 0 < number < 21:
        return number
    raise ValueError(f"Not acceptable value for limit {number}")


QUERY_PARAMS = {
    "offset": {decorators.VALIDATOR: int, decorators.DESTINATION: "skip"},
    "limit": {decorators.VALIDATOR: _limit_validator},
}
