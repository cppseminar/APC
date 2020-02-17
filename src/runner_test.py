"""Module containing tests for runner modules."""
import gc
import os
import subprocess

from unittest.mock import MagicMock

import pytest

import runner

# pylint: disable=missing-docstring
# pylint: disable=no-self-use
# pylint: disable=redefined-outer-name


class TimeoutException(subprocess.TimeoutExpired):
    """TimeoutExpired doesn't have empty constructor.

    It doesn't work well with mocks.  This ugly solution is only thing I could
    think of.
    """

    def __init__(self):
        """Call super init with some shitty values."""
        super().__init__(cmd="testing", timeout=1)


###################################
#            FIXTURES             #
###################################


@pytest.fixture
def runnable():
    """Create Runnable event."""
    def _pick_id(ident: str):
        return runner.Runnable(identification=ident,
                               exe_path='aaa',
                               name='student 1')
    return _pick_id


@pytest.fixture
def run_patcher(monkeypatch):
    """Return mock similar to completed process."""
    return_mock = MagicMock()
    return_mock.returncode = 0
    mock = MagicMock(return_value=return_mock)
    monkeypatch.setattr("runner.subprocess.run", mock)
    return return_mock, mock

@pytest.fixture(autouse=True)
def default_fixture():
    """We are often playing with waekrefs, so make it more clear."""
    gc.collect()
    yield
    gc.collect()

###################################
#          END FIXTURES           #
###################################


@pytest.mark.skip
class TestCompilerFilter:
    def test_settings(self):
        pass


# pylint: disable=unused-argument
class TestRunnerModule:
    """Tests for runner module."""

    def test_filter_bad_event(self, runnable, run_patcher):
        """Accept only events with correct identification."""
        module = runner.RunnerModule('test')
        module.set('input_identification', 'abc')
        module.set('output_identification', 'abc')
        module.set('args', '[]')
        assert module.handle_event(runnable('abc'))
        assert not module.handle_event(runnable('abcd'))

    def test_call_args(self, runnable, run_patcher):
        """Test argument passing to subprocess.run."""
        module = runner.RunnerModule('test')
        module.set('input_identification', 'abc')
        module.set('output_identification', 'abc')
        module.set('args', r'["abc", "c:\\users\\"]')
        executable = runnable('abc')
        module.handle_event(executable)
        _, run_mock = run_patcher
        run_mock.assert_called_once()
        assert run_mock.call_args[0][0] == [
            executable.exe_path, 'abc', "c:\\users\\"
        ]

    def test_timer_fail(self, runnable, run_patcher, monkeypatch):
        """Test return when timer fails."""
        _, run_mock = run_patcher
        module = runner.RunnerModule('test')
        module.set('input_identification', 'abc')
        module.set('output_identification', 'abd')
        module.set('args', r'["abc", "c:\\users\\"]')
        executable = runnable('abc')
        mock = MagicMock()
        monkeypatch.setattr(module, "send", mock)
        module.handle_event(executable)
        mock.assert_called_once()
        assert mock.call_args[0][0].timeout is False
        assert mock.call_args[0][0].identification == 'abd'

        run_mock.side_effect = TimeoutException

        module.handle_event(executable)
        assert mock.call_count == 2
        assert mock.call_args[0][0].timeout is True
        assert mock.call_args[0][0].identification == 'abd'

    @pytest.mark.skip
    def test_run_times(self, runnable, run_patcher):
        """Test whether process gets called given times."""
        pass

    def test_cleanup(self, runnable, run_patcher, monkeypatch):
        """Test whether cleanup works properly."""
        module = runner.RunnerModule('test')
        module.set('input_identification', 'abc')
        module.set('output_identification', 'abc')
        module.set('args', '[]')
        module.set('cleanup', 'True')
        executable = runnable('abc')
        mock = MagicMock()
        with monkeypatch.context() as context:
            context.setattr(module, "send", mock)
            module.handle_event(executable)
        file1 = mock.call_args[0][0].output_file
        file2 = mock.call_args[0][0].error_file
        assert os.path.exists(file1)
        assert os.path.exists(file2)
        del mock
        gc.collect()
        assert not os.path.exists(file1)
        assert not os.path.exists(file2)

    def test_cleanup_false(self, runnable, run_patcher, monkeypatch):
        """Test if cleanup settings preserves files."""
        module = runner.RunnerModule('test')
        module.set('input_identification', 'abc')
        module.set('output_identification', 'abc')
        module.set('args', '[]')
        module.set('cleanup', 'False')
        executable = runnable('abc')
        mock = MagicMock()
        with monkeypatch.context() as context:
            context.setattr(module, "send", mock)
            module.handle_event(executable)
        file1 = mock.call_args[0][0].output_file
        file2 = mock.call_args[0][0].error_file
        assert os.path.exists(file1)
        assert os.path.exists(file2)
        del mock
        del module
        gc.collect()
        assert os.path.exists(file1)
        assert os.path.exists(file2)
        os.unlink(file1)
        os.unlink(file2)


# pylint: enable=unused-argument
