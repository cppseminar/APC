"""Module containing classes responsible for running executables"""
import dataclasses
import os

import compiler
import infrastructure

_logger = infrastructure.set_logger(__name__)


@dataclasses.dataclass
class Runnable(infrastructure.Event):
    exe_path: str
    group: str  # Sub Identifier used by modules
    name: str  # Something like student's name
    platform: compiler.Platform


class CompilerFilter(infrastructure.Module):
    """Catch all events from compiler and transform some into runnables"""
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
                     group=self.settings['group'],
                     name=event.identifier,
                     platform=event.platform)
        self.send(r)


class TestRun:

    INPUT_FILE_NAME = "input.txt"
    EXE_NAME = "main.exe"
    STDOUT = "cout.txt"
    STDERR = "cerr.txt"
    DIFF = "outdiff.txt"

    def __init__(self, exe_path, input_file, expected_output, args=[], id="", folder=None):
        # Args
        self.expected_output = expected_output
        self.input_file = str(input_file)
        self.path = None
        self.orig_exe = exe_path
        self.args = self.input_file_magic(input_file, args)
        self.id = str(id)
        # Executable
        self.exit_code = 0
        self._executed = False
        self.run_time = None
        # Helpers
        self.folder = None
        self.parent_folder = folder
        self.diff = ""
        self._clean = True
        self.completed_process = None
        # asserts
        assert os.path.exists(exe_path)
        assert os.path.exists(input_file)
        assert os.path.exists(expected_output)

    def input_file_magic(self, input_file, args):
        indices = [i for i, s in enumerate(args) if input_file == s]
        new = args[:]
        for index in indices:
            new[index] = self.INPUT_FILE_NAME
        return new

    def run(self, max_time=None, test_runs=1):
        assert test_runs > 0
        time_sum = 0
        for _ in range(int(test_runs)):
            ret = self._run_internal(max_time=max_time)
            time_sum += ret.run_time
            if not ret:
                return ret
        self.run_time = time_sum / int(test_runs)

    def _run_internal(self, max_time=None):
        self._cleanup()
        self._prepare_folder()

        if settings.SETTINGS.verbose:
            print("Running program")

        self.completed_process = None

        def runProcess():
            with contextlib.suppress(subprocess.TimeoutExpired):
                self.completed_process = subprocess.run([self.path] + self.args,
                    timeout=max_time,
                    text=True,
                    capture_output=True,
                    cwd=self.folder)
            self._executed = True

        self.run_time = time.time()
        runProcess()
        self.run_time = time.time() - self.run_time

        if not self.completed_process: # Timeout errro
            self.exit_code = -1
            if settings.SETTINGS.verbose:
                print("Timeout expired")
            return self
        if settings.SETTINGS.verbose:
            print("Finished running")
        ## Program finished
        self.exit_code = self.completed_process.returncode
        self.diff = compare_strings(self.completed_process.stdout,
            transform_arg_to_str(self.expected_output))
        if not self.diff and self.exit_code == 0: # Fine
            return self
        return self

    def __bool__(self):
        return self._executed and self.exit_code is 0 and not self.diff

    def _cleanup(self):
        if self._clean and self.folder:
            shutil.rmtree(self.folder, ignore_errors=True)
            self.folder = None

    def __del__(self):
        self._cleanup()

    def __str__(self):
        ret = f"Run {self.id} success {self.__bool__()}, exit {self.exit_code} (-1 for time) ({self.run_time})"
        return ret

    def save_logs(self) -> str:
        """Return path, on which details about this run are saved"""
        self._clean = False
        if self.completed_process and self.completed_process.stdout:
            with open(os.path.join(self.folder, self.STDOUT), "w") as f:
                f.write(self.completed_process.stdout)
        if self.completed_process and self.completed_process.stderr:
            with open(os.path.join(self.folder, self.STDERR), "w") as f:
                f.write(self.completed_process.stderr)
        if self.completed_process is not None and self.diff:
            with open(os.path.join(self.folder, self.DIFF), "w") as f:
                f.write(self.diff)

        with open(os.path.join(self.folder, "cmd.bat"), "w") as f:
            cmd = f"@ cd \"{(self.folder)}\"\n"
            cmd += f"@ \"{(self.path)}\" "
            cmd += " ".join(shlex.quote(i) for i in self.args)
            f.write(cmd)

        return self.folder

    def _prepare_folder(self):
        self.folder = tempfile.mkdtemp(prefix="test_run_" + self.id + "_",
                                       dir=self.parent_folder)
        if not os.path.exists(self.folder):
            raise OSError("Cannot create temp folder")
        shutil.copy2(self.input_file, os.path.join(self.folder, self.INPUT_FILE_NAME))
        self.path = os.path.join(self.folder, self.EXE_NAME)
        shutil.copy2(self.orig_exe, self.path)
