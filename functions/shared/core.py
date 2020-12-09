"""Functions without application logic, required in multiple modules."""
from abc import ABC
import dataclasses
import datetime
import functools
import logging
import json
import typing
import re


from bson import ObjectId
from pymongo.cursor import Cursor
from pymongo.command_cursor import CommandCursor


def cerberus_object_id_validator(field, value, error):
    """Cerberus object id validator."""
    if not ObjectId.is_valid(value):
        error(field, "value doesn't seem like object id")

class DataclassDict(ABC):
    """Base class for all of our mongo models.

    map_item and filter_item can be overriden, to modify output.
    """

    def __iter__(self):
        return iter(
            map(
                self.map_item,
                filter(self.filter_item, dataclasses.asdict(self).items()),
            )
        )

    def map_item(self, item):
        """Called on each field. Able to change key or value."""
        key, value = item
        return key, value

    def filter_item(self, _item):
        """Called before map_items. You can disable output for some fields, by
        returning False."""
        return True

@dataclasses.dataclass
class ModelBase(DataclassDict):
    _id: ObjectId



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
        if isinstance(o, ModelBase):
            return dict(o)
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


def empty_dataclass_dict(klass):
    """Try to get dict from dataclass, with default values.

    If default value cannot be instantiated, returns empty string as value.

    WARNING: This should be used only with simple types (e.g. what you store in
             db), as it will often try to call constructors on types.
    """
    if not dataclasses.is_dataclass(klass):
        raise TypeError("Not a dataclass")

    def _get_key_value(field: dataclasses.Field):
        key = field.name
        if field.default is not dataclasses.MISSING:
            return key, field.default
        if field.default_factory is not dataclasses.MISSING:  # type: ignore
            return key, field.default_factory()  # type: ignore
        try:
            return key, field.type()
        except:
            pass
        return key, ""

    return dict(map(_get_key_value, dataclasses.fields(klass)))

@functools.singledispatch
def mongo_filter_errors(obj, converter):
    """Call converter on obj and ignore failed objects.

    Returns result of converter. If converter raises Exception, None will be
    returned.
    If obj is list, converter is called on each element. Those which raise
    exceptions are skipped.
    """
    if obj is None:
        return None
    try:
        return converter(obj)
    except Exception as error:
        logging.error("During parsing db data (single): %s", error)
        logging.error("Method %s", converter)
        logging.error("Value %s", obj)
        return None


@mongo_filter_errors.register(Cursor)
@mongo_filter_errors.register(CommandCursor)
@mongo_filter_errors.register(list)
def _mongo_list_ignore_errors(obj_list: Cursor, converter):
    for item in obj_list:
        try:
            yield converter(item)
        except Exception as error:
            # Skip this entry in list. We will only log error and continue
            logging.error("During parsing db data (iter): %s", error)
            logging.error("Method %s", converter)
            logging.error("Value %s", item)
