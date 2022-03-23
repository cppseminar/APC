"""Module containing classes responsible for running executables."""

import dataclasses
import json
import os
import subprocess
import time
import tempfile
import weakref


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

    identification: str = ""  # Id for machine
    output_file: str = ""
    error_file: str = ""
    exit_code: int = 1
    run_time: int = 0
    timeout: bool = True
    name: str = ''  # Name of student

    @staticmethod
    def cleanup(*args):
        """Delete files in args."""
        for file_name in args:
            try:
                os.unlink(file_name)
            except FileNotFoundError as error:
                _logger.info("File already deleted. %s", str(error))


class CompilerFilter(infrastructure.Module):
    """Catch all events from compiler and transform some into runnables."""

    SETTINGS = {
        'filter': list(compiler.Platform),
        'group': infrastructure.AnyStringParser()
    }

    def __init__(self, name):
        """Register for event."""
        super().__init__(name)
        self.register_event(compiler.CompilerEvent)

    def handle_internal(self, event: compiler.CompilerEvent):
        """Let forward only events without errors."""
        if event.errors:
            _logger.info(f"{event.identifier} {event.platform.name} has errors"
                         f" it won't be forwarded")
        if event.platform != self.settings['filter']:
            _logger.debug(f"{event.identifier} {event.platform.name} stopping "
                          f"would accept {self.settings['filter'].name}")
            return False
        _logger.debug(f"{event.identifier} {event.platform.name} will send")

        r = Runnable(exe_path=event.exe_path,
                     name=event.identifier,
                     identification=self.settings['group'])
        self.send(r)


class RunnerModule(infrastructure.Module):
    """Run compiled binary and produce RunOutput (event)."""

    SETTINGS = {
        'input_identification': infrastructure.AnyStringParser(),
        'output_identification': infrastructure.AnyStringParser(),
        'args': infrastructure.JsonListParser(),
        # 'run_times': [1, 3, 5],  # in init
        'max_time': infrastructure.AnyIntParser(default=10),
        # 'cleanup' = [True, False],  # In init,
        'stdin': compiler.FilePathParser(),
    }

    def __init__(self, name):
        """Parse SETTINGS and add some more."""
        super().__init__(name=name)
        self.register_event(Runnable)
        self.register_setting('cleanup', values=[True, False], default=True)
        # self.register_setting('run_times', values=[1, 3, 5], default=1)

    def _create_work_folder(self):
        """Little hack to put folder setting into settings."""
        try:
            self.settings["folder"]
        except infrastructure.ConfigError:
            self.register_setting(
                "folder",
                parser=infrastructure.TmpFolderCreator(
                    cleanup=self.settings['cleanup'],
                    name_parts=[
                        self.__class__.__name__,
                        self.settings["input_identification"],
                        self.settings["output_identification"],
                    ],
                ),
            )

    def handle_internal(self, event: Runnable):
        """Check if we want this event and execute."""
        if event.identification != self.settings['input_identification']:
            return False
        self._create_work_folder()
        # TODO: This really should't be used here.  Let's do some refactoring
        creator = infrastructure.TmpFolderCreator(
            cleanup=False, name_parts=[event.name, event.identification],
            directory=self.settings['folder'])
        folder = creator.default
        new_event = self.run_process(event, folder)
        self.notify(self._create_notification(new_event))
        self.send(new_event)
        return True

    def run_process(self, event, folder):
        """Run given executable and measure time."""
        arguments = json.loads(self.settings['args'])
        stdout_file = tempfile.NamedTemporaryFile(prefix='stdout',
                                                  dir=folder,
                                                  delete=False)

        stderr_file = tempfile.NamedTemporaryFile(prefix='stderr',
                                                  dir=folder,
                                                  delete=False)

        ret = None
        stdin = self.settings["stdin"]
        if stdin == "None":
            stdin = None
        else:
            stdin = open(stdin, "r")
            weakref.finalize(stdin, lambda: stdin.close())

        try:  # Try - exception on timeout
            run_time = time.time()
            process = subprocess.run([event.exe_path] + arguments,
                                     timeout=int(self.settings['max_time']),
                                     text=True,
                                     cwd=folder,
                                     stdout=stdout_file,
                                     stderr=stderr_file,
                                     stdin=stdin,
                                     check=False)
            run_time = time.time() - run_time
            ret = RunOutput(
                output_file=stdout_file.name,
                error_file=stderr_file.name,
                run_time=run_time,
                timeout=False,
                exit_code=process.returncode,
                identification=self.settings['output_identification'],
                name=event.name)
            return ret

        except subprocess.TimeoutExpired:
            ret = RunOutput(
                timeout=True,
                identification=self.settings['output_identification'],
                name=event.name,
                output_file=stdout_file.name,
                error_file=stderr_file.name,
            )
            return ret
        finally:
            stdout_file.close()
            stderr_file.close()
            if self.settings['cleanup'] is True:
                weakref.finalize(ret, ret.cleanup,
                                 str(stdout_file.name), str(stderr_file.name))

    def _create_notification(self, event):
        """Given event RunOutput, create notification for loggers."""
        identificator = ('[' + self.__class__.__name__ + '] ' + self.name +
                        ' - ' +  event.name + "_" + event.identification + "_")
        if event.timeout:
            return infrastructure.Notification(
                message=f'{identificator} '
                        f'failed on time',
                severity=infrastructure.MessageSeverity.ERROR)

        if event.exit_code != 0:
            return infrastructure.Notification(
                message=f'{identificator} '
                        f'exit code {event.exit_code}. Run {event.run_time}s',
                severity=infrastructure.MessageSeverity.WARNING)

        return infrastructure.Notification(
            message=f'{identificator} '
                    f'run time {event.run_time}s',
            severity=infrastructure.MessageSeverity.INFO)


class StdPrinter(infrastructure.Module):
    SETTINGS = {"input_identification": infrastructure.AnyStringParser()}

    def __init__(self, name):
        """Register event."""
        super().__init__(name)
        self.register_event(RunOutput)


    def handle_internal(self, event: RunOutput):
        """Check if file is sorted according to sort indices."""
        if event.identification != self.settings["input_identification"]:
            return False
        identificator = "[" + self.__class__.__name__ + f"] - {self.name}"
        content = ""

        with open(event.output_file, "r") as stdout:
            content = stdout.read()
        if not content:
            self.notify(
                infrastructure.Notification(
                    message=f"{identificator} - Empty output",
                    severity=infrastructure.MessageSeverity.WARNING,
                )
            )
            return True
        self.notify(
            infrastructure.Notification(
                message=f"{identificator} - Showing output",
                severity=infrastructure.MessageSeverity.INFO,
                payload=content,
            )
        )
        return True




