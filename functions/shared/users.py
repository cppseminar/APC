"""User support functions and definitions."""
import dataclasses
import typing

from . import mongo


@dataclasses.dataclass
class User:
    """Representation of authenticated user."""
    email: str
    is_admin: bool = False
    roles: typing.List = dataclasses.field(default_factory=list)


def get_user(email: str):
    """Return user instance from db. If ne create new one."""
    return mongo.MongoUsers.get_user(email)
