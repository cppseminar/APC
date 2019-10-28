import tempfile
import contextlib
import os
import subprocess
import shutil
import shlex
import xml.etree.ElementTree as ET

from typing import Dict, Iterable
from enum import IntEnum, unique, auto
from difflib import Differ

import settings

def parse_env(lines: Iterable[str]):
    environment = {}
    for line in lines.split("\n"):
        if not line:
            continue
        keyword, entry = line.split("=", maxsplit=1)
        environment[keyword] = entry
    return environment

@unique
class Platform(IntEnum):
    x64_Debug = auto()
    x64_Release = auto()
    x32_Debug = auto()
    x32_Release = auto()

class Executable:
    LOG = 'compilation.txt'

    def __init__(self, file_name, warnings=[], errors=[]):
        self.file = file_name
        self.warnings = warnings
        self.errors = errors

    def __bool__(self):
        return self.file and os.path.exists(self.file) and not self.errors

    def __str__(self):
        ret = ""
        if not self.__bool__():
            ret += "[FAIL]\n"
        elif len(self.warnings):
            ret += "[WARNINGS]\n"
        else:
            return "[OK]"

        return ret + f"   #errors {len(self.errors)} #warnings {len(self.warnings)}"

    def get_log(self):
        ret  = "WARNINGS\n"
        ret += "-----------\n"
        ret += "     \n     ".join([str(i) for i in self.warnings])
        ret += "\nERRORS\n"
        ret += "-----------\n"
        ret += "     \n     ".join([str(i) for i in self.errors])
        return ret



class Compiler:
    BAT_PATH = r'..\msbuild\run.bat'
    EXE_NAME = 'main.exe'
    WARNINGS = 'warnings.xml'
    ERRORS = 'errors.xml'
    BUILD_MAP = {
        Platform.x64_Debug.value   : "Debug_x64",
        Platform.x64_Release.value : "Release_x64",
        Platform.x32_Debug.value   : "Debug_Win32",
        Platform.x32_Release.value : "Release_Win32",
    }

    def __init__(self, file_names, folder=None, identificator=""):
        if not file_names:
            raise ValueError("At least one file for compilation is necessary")
        self.file_names = file_names
        if isinstance(file_names, str):
            self.file_names = [file_names]
        self.file_names = [os.path.abspath(name) for name in self.file_names]

        self.directory = tempfile.mkdtemp(prefix="compiler_" + identificator + "_",
                                          dir=folder)
        self.compiled = False
        self._clean = True

    def _srsly_compile(self):
        args = [self.directory] + self.file_names
        compiler = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.BAT_PATH)
        if settings.SETTINGS.verbose:
            print(f"Starting compilation, args {compiler} {args}")
        completed_process = subprocess.run([compiler] + args,
            capture_output=True,
            cwd=self.directory)
        if completed_process.returncode != 0:
            self._clean = False
            raise RuntimeError("Compiler failed!! :(")

    def compile(self, platform):
        if not self.compiled:
            self._srsly_compile()
            self.compiled = True
        # Let's find and parse files for this build
        folder_path = os.path.join(self.directory, self.BUILD_MAP[platform])
        if not os.path.exists(folder_path):
            self._clean = False
            raise FileNotFoundError(f"Compiler fail {self.directory} {platform}")
        exe_path = os.path.join(folder_path, self.EXE_NAME)
        warnings_path = os.path.join(folder_path, self.WARNINGS)
        errors_path = os.path.join(folder_path, self.ERRORS)
        warnings = self.get_xml_entries(warnings_path)
        errors = self.get_xml_entries(errors_path)
        exe_exists = os.path.exists(exe_path)
        assert bool(exe_exists) != bool(errors)
        return Executable(exe_path, warnings, errors)

    def get_xml_entries(self, xml_path):
        root = [{}] # Fix for FileNotFound
        with contextlib.suppress(FileNotFoundError):
            tree = ET.parse(xml_path)
            root = tree.getroot()
        return [i.items() for i in root]


def compare_strings(input_string, output_string):
    """Returns empty string, if strings match. Else returns complete diff"""
    inputs = input_string.split("\n")
    outputs = output_string.split("\n")
    d = Differ()
    ret = []
    found_error = False
    # Don't bother with empty line in the end
    if outputs and not outputs[-1]:
        del outputs[-1]

    if inputs and not inputs[-1]:
        del inputs[-1]

    for line in d.compare(outputs, inputs):
        ret.append(line)
        if line[0:2] != "  ":
            found_error = True

    if found_error:
        return "\n".join(ret)
    return ""


def transform_arg_to_str(something) -> str:
    """Converts something to str. Something is either None, or file path
    or string"""
    if not something:
        return ""
    if os.path.exists(something):
        with open(something, "r") as f:
            return f.read()
    # TODO: Support for string
    raise ValueError(f"Arg cannot be converted {str(something)}")


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
        self.path = exe_path
        self.args = self.input_file_magic(input_file, args)
        self.id = str(id)
        # Executable
        self.exit_code = 0
        self._executed = False
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

    def run(self, max_time=None):
        self._cleanup()
        self._prepare_folder()

        if settings.SETTINGS.verbose:
            print("Running program")

        self.completed_process = None
        with contextlib.suppress(subprocess.TimeoutExpired):
            self.completed_process = subprocess.run([self.path] + self.args,
                timeout=max_time,
                text=True,
                capture_output=True,
                cwd=self.folder)
        self._executed = True

        if not self.completed_process: # Timeout errro
            self.exit_code = -1
            if settings.SETTINGS.verbose:
                print("Timeout expired")
            return
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
        ret = f"Run {self.id} success {self.__bool__()}, exit {self.exit_code} (-1 for time)"
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
        new_exe = os.path.join(self.folder, self.EXE_NAME)
        shutil.copy2(self.path, new_exe)
        self.path = new_exe

if __name__ == "__main__":
    pass
