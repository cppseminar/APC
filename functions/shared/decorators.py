"""Decorators for functions working with http."""
import inspect
import logging
import functools
import typing

import azure.functions as functions
from bson.objectid import ObjectId

from . import common
from . import users
from .http import response_server_error, response_client_error


def login_required(func: typing.Callable):
    """Decorator handling users.

    If your function uses 'user' as keyword parameter, it will be filled with
    current user instance.
    """
    set_user = False
    user_in_args = "user"  # Keyword arg that gets filled
    if user_in_args in inspect.signature(func).parameters:
        set_user = True  # Wrapped function does have 'user' keyword

    @functools.wraps(func)
    def _user_wrapper(req: functions.HttpRequest, *args, **keyword_args):
        email = req.headers.get(common.HEADER_EMAIL, "")
        if not users.validate_email(email):
            logging.warning(
                "Rejecting not an email %s in %s field", email, common.HEADER_EMAIL
            )
            return response_server_error()
        # User is authenticated, now get his details, if function is interested
        # in them
        if set_user:
            user = users.get_user(email)
            keyword_args[user_in_args] = user
        return func(req, *args, **keyword_args)

    return _user_wrapper


VALIDATOR = "validator"
DESTINATION = "dest"

def object_id_validator(value):
    """Return object id as ObjectId object, or raise error."""
    if not ObjectId.is_valid(value):
        raise RuntimeError(f"Value {str(value)} doesn't look like object ID")
    return ObjectId(value)



def _get_mapper(settings: dict):
    def _internal(entry: typing.Tuple[str, dict]):
        # We expect entry[0] to be in dict, as it is reponsibility of caller
        # to not call this function relentlessly
        entry_settings = settings[entry[0]]
        destination = entry_settings.get(DESTINATION, entry[0])
        value_validator = entry_settings.get(VALIDATOR, lambda x: x)
        return str(destination), value_validator(entry[1])

    return _internal


def validate_parameters(route_settings: typing.Dict[str, dict] = None,
                        query_settings: typing.Dict[str, dict] = None):
    """
    Decorator for request argument/parameter validation.

    This decorator expects, that your function will have as first positional
    paramter azure.functions.HttpRequest object.

    Additional paramters (not configured in here) are ignored

    Parameters
    ----------
     route_setting - settings for arguments in route (uri/{parameter}/...)
     query_settings - settings for additional arguments in uri (behind ?)

    Configuration
    -------------
     Settings are dict.  Keys are names of expected arguments. Value is dict
     with specific format.

     Under key VALIDATOR - this is constant defined in this module - you must
     specify function which will be called with value of parameter and her
     return will be considered 'validated' argument. If instead arugment would
     be invalid, just raise RuntimeError.

     Under key DESTINATION - contant from this module - you may specify string,
     under which validated value will be passed to decorated function as kw
     argument. If you don't use this argument, key from settings will be used
     as destination.

    """
    # Route params
    query_mapper = _get_mapper(query_settings or {})
    route_mapper = _get_mapper(route_settings or {})

    def _func_call(func: typing.Callable):
        @functools.wraps(func)
        def _wrapper(req: functions.HttpRequest, *args, **kwargs):
            # At first let's throw away not requested/unused args
            route_args = filter(
                lambda tup: tup[0] in route_settings,  # type: ignore
                req.route_params.items(),
            )
            query_args = filter(
                lambda tup: tup[0] in query_settings,  # type: ignore
                req.params.items(),
            )
            # Now validate / map rest
            try:
                kwargs.update(dict(map(query_mapper, query_args)))
                kwargs.update(dict(map(route_mapper, route_args)))
            except Exception as error: # pylint: disable=W0703
                # Let's assume validator threw some solid description
                logging.warning("Error during parsing http params %s", error)
                return response_client_error()
            return func(req, *args, **kwargs)

        return _wrapper

    return _func_call
