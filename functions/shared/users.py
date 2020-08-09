"""User support functions and definitions."""
import dataclasses
import re
import typing

from . import mongo


@dataclasses.dataclass
class User:
    """Representation of authenticated user."""
    email: str
    is_admin: bool = False
    roles: typing.List = dataclasses.field(default_factory=list)


def validate_email(email_address: str):
    """Return true if param looks like email address.

    This is in no way verification of some standards for email address, instead
    it is general check, if we are not sending some bs through our api.
    """
    ret = re.match(r"^[a-z0-9]+@[a-z0-9]+\.[a-z]{2,5}$", email_address)
    if ret:
        return True
    return False


def get_user(email: str):
    """Return user instance from db. If ne create new one."""
    return mongo.MongoUsers.get_user(email)
