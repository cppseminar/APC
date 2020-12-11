"""Tests for shared module testers."""
import base64

import pytest
import functions.shared.testers as testers
import functions.shared.common as common


class TestTesterConstruct:
    """Tester construction tests."""

    @staticmethod
    def get_dict():
        secret = base64.encodebytes("Hello".encode("ascii"))
        return {
            common.TESTER_PARTITION_KEY: "vm-name",
            common.TESTER_ROW_KEY: "abcd",
            common.TESTER_URL: "abcd",
            common.TESTER_START_URL: "abcd",
            common.TESTER_STOP_URL: "abcd",
            common.TESTER_SECRET: secret.decode("ascii"),
        }

    def test_ok(self):
        entry = self.get_dict()
        del entry[common.TESTER_START_URL]
        del entry[common.TESTER_STOP_URL]
        result = testers.dict_to_tester(entry)
        assert result.name == "vm-name"
        assert result.secret == b"Hello"

    def test_missing_url(self):
        entry = self.get_dict()
        del entry[common.TESTER_URL]
        with pytest.raises(ValueError):
            testers.dict_to_tester(entry)

    def test_timeout_set(self):
        entry = self.get_dict()
        result = testers.dict_to_tester(entry)
        assert result.stop_after is None
        result = testers.dict_to_tester(entry)
        entry[common.TESTER_STOP_AFTER] = 10
        result = testers.dict_to_tester(entry)
        assert result.stop_after == 10
        # Now some errors
        del entry[common.TESTER_START_URL]
        with pytest.raises(ValueError):
            result = testers.dict_to_tester(entry)


    def test_not_configured(self):
        """When stop after is not configured, start and stop must be None."""
        entry = self.get_dict()
        result = testers.dict_to_tester(entry)
        assert result.name
        assert result.stop_after is None
        assert result.stop_url is None
        assert result.start_url is None
