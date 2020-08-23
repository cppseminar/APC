"""Functions without application logic, required in multiple modules."""
import datetime
import json
import typing
import re


from bson import ObjectId


def schema_object_id_validator(field, value, error):
    """Cerberus object id validator."""
    if not ObjectId.is_valid(value):
        error(field, "value doesn't seem like object id")


class MongoEncoder(json.JSONEncoder):
    """Json encoder extension, able to encode mongo types.

    This is better than default bson tools, because it allows us to hide mongo
    specific entries, like $oid or $date.
    """

    def default(self: json.JSONEncoder, obj: typing.Any):
        """Detect and encode mongo types."""
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            new_date = obj.replace(tzinfo=datetime.timezone.utc)
            return new_date.isoformat()
        return json.JSONEncoder.default(self, obj)


def is_email(address: str):
    """Check if address is email suitable for our needs.

    Note: This is in no way complete and probably not even correct validation
          of email address.  But it is format in which we expect our users
          will have their email addresses.
    """
    ret = re.match(r"^[a-z0-9\.]+@([a-z0-9]+\.)+[a-z]{2,5}$", address)
    if ret:
        return True
    return False
