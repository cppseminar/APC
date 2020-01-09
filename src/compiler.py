import contextlib
import dataclasses
import os
import pathlib
import shutil
import subprocess
import tempfile
import weakref
import xml.etree.ElementTree as ET

from typing import Iterable, List
from enum import IntEnum, unique, auto
from difflib import Differ

import constants
import infrastructure
import library
import settings


_logger = infrastructure.set_logger(__name__)


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
        ret = "WARNINGS\n"
        ret += "-----------\n"
        ret += "     \n     ".join([str(i) for i in self.warnings])
        ret += "\nERRORS\n"
        ret += "-----------\n"
        ret += "     \n     ".join([str(i) for i in self.errors])
        return ret


class FilePathParser(infrastructure.SettingsParser):
    def is_valid(self, value):
        return value == 'None' or os.path.exists(value)

    def get_options(self):
        return ["<any file/folder or None>"]

    @property
    def default(self):
        """This shall cause error"""
        return infrastructure.MISSING


@dataclasses.dataclass
class SourceFileEvent(infrastructure.Event):
    file_names: List[str]


class CppFinder(infrastructure.Module):
    SETTINGS = {
        "folder_path": FilePathParser(),
        "file_path": FilePathParser(),
    }

    @staticmethod
    def _filter_cpp_files(files: Iterable):
        return library.filter_files(files, wildcard='*.c*')

    def __init__(self, name):
        super().__init__(name)
        self.register_event('start')
        self.files = None

    def _process_settings(self):
        """Check whether user config is ok"""
        if self.settings['folder_path'] != 'None':
            all_files = library.iterate_files(self.settings['folder_path'],
                                              include_dirs=False)
            self.files = list(self._filter_cpp_files(all_files))
        if self.settings['file_path'] != 'None':
            if self.files is not None:
                raise infrastructure.ConfigError(
                    f"In {self.__class__.__name__} specify only one path")
            self.files = [self.settings['file_path']]

    def handle_internal(self, event):
        self._process_settings()
        self.files = list(map(lambda x: x.resolve(), self.files))
        for file_name in self.files:
            notif = infrastructure.Notification(f"Found file/s {file_name}")
            self.notify(notif)
            event = SourceFileEvent([file_name])
            self.send(event)

def file_name_to_identifier(file_name):
    return pathlib.PurePath(file_name).stem

@dataclasses.dataclass
class CompilerEvent(infrastructure.Event):
    exe_path: str
    platform: Platform
    warnings: List[str]
    errors: List[str]
    identifier: str  # file name - probably not unique


class Compiler(infrastructure.Module):
    SETTINGS = {
        'folder_path': FilePathParser(),
        # cleanup - in init
    }
    BAT_PATH = r'..\msbuild\run.bat'
    EXE_NAME = 'main.exe'
    WARNINGS = 'warnings.xml'
    ERRORS = 'errors.xml'
    BUILD_MAP = {
        Platform.x64_Debug.value:   "Debug_x64",
        Platform.x64_Release.value: "Release_x64",
        Platform.x32_Debug.value:   "Debug_Win32",
        Platform.x32_Release.value: "Release_Win32",
    }

    def __init__(self, name):
        super().__init__(name)
        self.register_event(SourceFileEvent)
        self.register_setting('cleanup', values=[True, False], default=True)
        self.file_names = []
        self.compiled = False

    def handle_internal(self, event: SourceFileEvent):
        self.directory = tempfile.mkdtemp(prefix="compiler_",
                                          dir=self.settings['folder_path'])
        if self.settings['cleanup']:
            weakref.finalize(self, shutil.rmtree, self.directory)

        self.file_names = list(map(str, event.file_names))
        self.handle_new_event(self.compile(Platform.x64_Debug))
        self.handle_new_event(self.compile(Platform.x64_Release))
        self.handle_new_event(self.compile(Platform.x32_Debug))
        self.handle_new_event(self.compile(Platform.x32_Release))
        self.compiled = False

    def _srsly_compile(self):
        args = [self.directory] + self.file_names
        compiler = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                self.BAT_PATH)
        _logger.debug("Compiling cwd %s %s", self.directory, [compiler] + args)
        completed_process = subprocess.run([compiler] + args,
                                           capture_output=True,
                                           cwd=str(self.directory))
        if completed_process.returncode != 0:
            logger.info(f'Compilation failed - {self.file_names}')
            self.notify(infrastructure.Notification(
                               message=f'Failed compilation{self.file_names}'))

            return False
        return True

    def compile(self, platform):
        if not self.compiled:
            if not self._srsly_compile():
                return Executable('', ['fail'], [])
            self.compiled = True
        # Let's find and parse files for this build
        folder_path = os.path.join(self.directory, self.BUILD_MAP[platform])
        if not os.path.exists(folder_path):
            _logger.warning(f"Compiler fail {self.directory} {platform}")
        exe_path = os.path.join(folder_path, self.EXE_NAME)
        warnings_path = os.path.join(folder_path, self.WARNINGS)
        errors_path = os.path.join(folder_path, self.ERRORS)
        warnings = '\n'.join(map(str, self.get_xml_entries(warnings_path)))
        errors = '\n'.join(map(str, self.get_xml_entries(errors_path)))
        exe_exists = os.path.exists(exe_path)

        assert bool(exe_exists) != bool(errors)
        if exe_exists:
            return CompilerEvent(exe_path,
                                 warnings=warnings,
                                 errors=errors,
                                 platform=platform,
                                 identifier=file_name_to_identifier(
                                     self.file_names[0]))
        return CompilerEvent(None,
                             warnings=warnings,
                             errors=errors,
                             platform=platform,
                             identifier=file_name_to_identifier(
                                 self.file_names[0]))

    def get_xml_entries(self, xml_path):
        root = [{}]  # Fix for FileNotFound
        with contextlib.suppress(FileNotFoundError):
            tree = ET.parse(xml_path)
            root = tree.getroot()
        return [i.items() for i in root]

    def handle_new_event(self, event: CompilerEvent):
        if not event.exe_path:
            self.notify(
                infrastructure.Notification(
                    f"Compilation failed for {self.file_names}, "
                    f"platform {event.platform.name}",
                    infrastructure.MessageSeverity.ERROR,
                    payload=event.errors))
            return  # Don't send event furhter

        if event.warnings:
            self.notify(
                infrastructure.Notification(
                    f"Compilation with warnings for {self.file_names} "
                    f"{event.platform.name}",
                    infrastructure.MessageSeverity.WARNING,
                    payload=event.warnings))
        else:
            self.notify(
                infrastructure.Notification(
                    f"Compilation success for {self.file_names} "
                    f"{event.platform.name}",
                    infrastructure.MessageSeverity.INFO))

        self.send(event)


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




if __name__ == "__main__":
    pass
