import unittest.mock
from unittest.mock import MagicMock
import pytest

from functions.shared.decorators import (
    login_required,
    validate_parameters,
    object_id_validator,
    VALIDATOR,
    DESTINATION,
)
from functions.shared.common import HEADER_EMAIL


class TestLoginRequired:
    @unittest.mock.patch("functions.shared.mongo.get_client")
    def test_no_login(self, mock):
        call_count = 0
        request = MagicMock()
        request.headers = {}

        def _fnc(req):
            nonlocal call_count
            call_count += 1

        login_required(_fnc)(request)
        assert mock.call_count == 0
        assert call_count == 0

    @unittest.mock.patch("functions.shared.mongo.get_client")
    def test_login(self, mock):
        call_count = 0
        request = MagicMock()
        request.headers = {HEADER_EMAIL: "abcd@efg.hij"}

        def _fnc(req):
            nonlocal call_count
            call_count += 1

        login_required(_fnc)(request)
        assert call_count == 1

        # We don't accept this as email
        request.headers = {HEADER_EMAIL: "abcd@efg"}
        login_required(_fnc)(request)
        assert call_count == 1
        assert mock.call_count == 0

    @unittest.mock.patch("functions.shared.mongo.get_client")
    def test_login_user_param(self, mock):
        call_count = 0
        request = MagicMock()
        request.headers = {HEADER_EMAIL: "abcd@efg.hij"}

        @login_required
        def _fnc(req, user=None):
            assert user
            nonlocal call_count
            call_count += 1

        _fnc(request)
        assert call_count == 1
        assert mock.call_count == 1


class TestValidateParameters:
    def test_empty_call(self):
        call_count = 0
        request = MagicMock()

        @validate_parameters()
        def _decorated(req: dict):
            nonlocal call_count
            call_count = 1

        _decorated(request)
        assert call_count == 1

    def test_param_extra(self):
        """This is expected to pass and silently ignore extra args."""
        result = None
        request = MagicMock()
        request.route_params = {"number": "bacd", "extraArg": 45}

        def _validator(value):
            return 243

        @validate_parameters(route_settings={"number": {VALIDATOR: _validator}})
        def _decorated(req, number=None):
            nonlocal result
            result = number

        _decorated(request)
        assert result == 243

    def test_route_param(self):
        result = None
        request = MagicMock()
        request.route_params = {"number": "bacd"}

        def _validator(value):
            return 243

        @validate_parameters(route_settings={"number": {VALIDATOR: _validator}})
        def _decorated(req, number=None):
            nonlocal result
            result = number

        _decorated(request)
        assert result == 243

    def test_error_param(self):
        """This should silently fail and return 400 bad request."""
        result = None
        request = MagicMock()
        request.route_params = {"number": "bacd"}

        def _validator(value):
            return int(value)

        @validate_parameters(route_settings={"number": {VALIDATOR: _validator}})
        def _decorated(req, number=None):
            nonlocal result
            result = number

        call_result = _decorated(request)
        assert result == None
        assert call_result.status_code == 400


    def test_remap_param(self):
        result = None
        request = MagicMock()
        request.route_params = {"number": "444"}

        def _validator(value):
            return int(value)

        @validate_parameters(route_settings={"number": {VALIDATOR: _validator, DESTINATION: "abcd"}})
        def _decorated(req, abcd=None):
            nonlocal result
            result = abcd

        call_result = _decorated(request)
        assert result == 444

def test_object_id_validator():
    with pytest.raises(Exception):
        object_id_validator("123")
    with pytest.raises(Exception):
        object_id_validator("asdf")
    assert object_id_validator("5f3172e94ccb2b29ecbf28e0")
