from unittest.mock import MagicMock
import pytest

from functions.shared.http import login_required
from functions.shared.common import HEADER_EMAIL




class TestLoginRequired:

    def test_no_login(self):
        call_count = 0
        request = MagicMock()
        request.headers = {}

        def _fnc(req):
            nonlocal call_count
            call_count += 1

        login_required(_fnc)(request)
        assert call_count == 0


    def test_login(self):
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

