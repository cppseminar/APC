import unittest.mock
from unittest.mock import MagicMock
import pytest

from functions.shared.decorators import login_required
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
