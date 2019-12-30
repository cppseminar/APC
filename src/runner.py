"""Module containing classes responsible for running executables."""

import contextlib
import dataclasses
import json
import subprocess
import time

import compiler
import infrastructure

_logger = infrastructure.set_logger(__name__)


@dataclasses.dataclass
class Runnable(infrastructure.Event):
    """Event created by compiler filter, handled by runner."""

    exe_path: str
    identification: str  # Sub Identifier used by modules
    name: str  # Something like student's name


@dataclasses.dataclass
class RunOutput(infrastructure.Event):
    """Event returned by runner, handled by evaluators."""

    identification: str
    output_file: str
    error_file: str
    exit_code: int
    timer_end: bool


class CompilerFilter(infrastructure.Module):
    """Catch all events from compiler and transform some into runnables."""

    SETTINGS = {
        'filter': list(compiler.Platform),
        'group': infrastructure.AnyStringParser()
    }

    def __init__(self, name):
        super().__init__(name)
        self.register_event(compiler.CompilerEvent)

    def handle_internal(self, event: compiler.CompilerEvent):
        if event.errors:
            _logger.info(f"{event.identifier} {event.platform.name} has errors"
                         f" it won't be forwarded")
        if event.platform != self.settings['filter']:
            _logger.debug(f"{event.identifier} {event.platform.name} stopping "
                          f"would accept {self.settings['filter']}")
            return False
        _logger.debug(f"{event.identifier} {event.platform.name} will send")

        r = Runnable(exe_path=event.exe_path,
                     identification=self.settings['group'],
                     name=event.identifier)
        self.send(r)


class RunnerModule(infrastructure.Module):
    """Run compiled binary and produce RunOutput (event)."""

    SETTINGS = {
        'input_identification': infrastructure.AnyStringParser(),
        'output_identification': infrastructure.AnyStringParser(),
        'args': infrastructure.JsonListParser(),
        # 'run_times': [1, 3, 5],
        'max_time': infrastructure.AnyIntParser(default=10)
    }

    def __init__(self, name):
        """Parse SETTINGS and add some more."""
        super().__init__(name=name)
        self.register_event(Runnable)
        self.register_setting('run_times', values=[1, 3, 5], default=1)

    def handle_internal(self, event: Runnable):
        """Check if we want this event and execute."""
        if event.identification != self.settings['input_identification']:
            return False
        return True

    def run_process(self, max_time=0):
        """Run given executable and measure time."""
        arguments = json.loads(self.settings['args'])
        run_time = time.time()
        subprocess.run()
        run_time = time.time() - run_time

