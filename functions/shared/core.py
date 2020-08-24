"""Functions without application logic, required in multiple modules."""
import dataclasses
import datetime
import json
import typing
import re


from bson import ObjectId


def cerberus_object_id_validator(field, value, error):
    """Cerberus object id validator."""
    if not ObjectId.is_valid(value):
        error(field, "value doesn't seem like object id")


class MongoEncoder(json.JSONEncoder):
    """Json encoder extension, able to encode mongo types.

    This is better than default bson tools, because it allows us to hide mongo
    specific entries, like $oid or $date.
    """

    def default(self: json.JSONEncoder, o: typing.Any):
        """Detect and encode mongo types."""
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            new_date = o.replace(tzinfo=datetime.timezone.utc)
            return new_date.isoformat()
        return json.JSONEncoder.default(self, o)


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


def instantiate_dataclass(klass, **kwargs):
    """Calls init on KLASS, with required subgroup of kwargs.

    Motivation for this function is, that you may have dictionary with lots of
    keys (for example result from db) and you want to create dataclass from it.
    Using standard init would throw exception, due to non-existing arguments.
    This function throws away those parameters, which are not in generated
    __init__ function.
    """
    if not dataclasses.is_dataclass(klass):
        raise TypeError("Not a dataclass")

    def _is_init_param(some_field: dataclasses.Field):
        return some_field.init

    fields = filter(_is_init_param, dataclasses.fields(klass))
    names = set(map(lambda x: x.name, fields))  # All field names in dataclass
    new_kwargs = [(arg[0], arg[1]) for arg in kwargs.items() if arg[0] in names]
    return klass(**dict(new_kwargs))
