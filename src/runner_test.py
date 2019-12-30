"""Module containing tests for runner modules."""
from unittest.mock import MagicMock, patch

import pytest

import compiler
import runner

# pylint: disable=missing-docstring
# pylint: disable=no-self-use

###################################
#            FIXTURES             #
###################################


@pytest.fixture
def runnable():
    """Create Runnable event."""
    def _pick_id(ident: str):
        return runner.Runnable(identification=ident,
                               exe_path='idk',
                               name='student 1')
    return _pick_id


@pytest.fixture
def completed_process():
    """Return mock similar to completed process."""
    return_mock = MagicMock()
    return_mock.returncode = 0
    mock = MagicMock(return_value=return_mock)
    return mock

###################################
#          END FIXTURES           #
###################################


@pytest.mark.skip
class TestCompilerFilter:
    def test_settings(self):
        pass


@pytest.mark.skip
class TestRunnerModule:
    """Tests for runner module."""

    def test_filter_bad_event(self, runnable, completed_process):
        """Accept only events with correct identification."""
        with patch('subprocess.run', new_callable=completed_process):
            module = runner.RunnerModule('test')
            module.set('input_identification', 'abc')
            assert module.handle_event(runnable('abc'))
            assert not module.handle_event(runnable('abcd'))

    def test_call_args(self, runnable, completed_process):
        """Test argument passing to subprocess.run."""
        module = runner.RunnerModule('test')
        module.set('input_identification', 'abc')
        module.set('output_identification', 'abc')
        module.set('args', '["abc", "c:\\users\\"]')
        print(completed_process().returncode)
        assert False

    def test_timer_fail(self, runnable, completed_process):
        """Test return when timer fails."""
        assert False

    def test_run_times(self, runnable, completed_process):
        """Test whether process gets called given times."""
        completed_process.side_effect=[1,3]
        print(completed_process())
        print(completed_process())
        assert False

    def test_measure_run_time(self, runnable, completed_process):
        """Test if time is measured correctly."""
        mock = MagicMock()
        mock.side_effects = [10, 15]
        module = runner.RunnerModule('test')
        module.set('input_identification', 'abc')
        module.set('output_identification', 'abc')
        module.set('args', '["abc"]')

