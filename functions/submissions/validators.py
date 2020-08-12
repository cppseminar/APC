"""Validation config and functions for submissions."""
from ..shared import decorators
from ..shared import core

POST_SCHEMA = {
    "files": {
        "type": "list",
        "required": True,
        "maxlength": 4,
        "minlength": 1,
        "items": [
            {
                "type": "dict",
                "require_all": True,
                "schema": {
                    "fileName": {
                        "type": "string",
                        "minlength": 4,
                        "maxlength": 250,  # This seems like reasonable size
                    },
                    "fileContent": {
                        "type": "string",
                        "minlength": 1,
                        "maxlength": 1024 * 100,  # 100KB max file size
                    },
                },
            }
        ],
    },
    "taskId": {
        "type": "string",
        "required": True,
        "empty": False,
        "check_with": core.schema_object_id_validator,
    },
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
