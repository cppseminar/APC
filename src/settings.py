"""This module will be for handling all setting in some nice way.  It should be
able to parse arguments, and later config files.  Basically you will just ask
this module for any setting you like"""

import argparse
import dataclasses
import collections

import infrastructure
from typing import List
import enum

SETTINGS = None

class Settings:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Compile list of files and run tests")
        parser.add_argument("-d", "--dir",
                            help="if used it is expected to use path to directory instead of files",
                            action="store_true")
        parser.add_argument('--test', help="path to the json file with test cases")
        parser.add_argument('--test-data', help="path to folder with test data", default='.')
        parser.add_argument('--output', help="path to otput directory")
        parser.add_argument('--verbose')
        parser.add_argument('files', nargs='+')
        args = parser.parse_args()

        self.files = args.files
        self.test_data = args.test_data
        self.test = args.test
        self.dir = args.dir
        self.output = self.get_output_dir(args.output)
        self.verbose = args.verbose
    
    def get_output_dir(self, output):
        if output is None:
            import tempfile
            return tempfile.mkdtemp(prefix='students')
        else:
            return output



SETTINGS = Settings()


class Config:
    def __init__(self):
        self.class_chain = collections.deque()

    def add_module(self, module_name):
        self.class_chain.append(module_name)

    def get_modules(self) -> List:
        return [self.class_chain]



@enum.unique
class Build(enum.IntEnum):
    x64_Debug = enum.auto()
    x64_Release = enum.auto()
    x32_Debug = enum.auto()
    x32_Release = enum.auto()

class CompilerEvent(infrastructure.Event):
    success: bool = False
    warnings: List[str] = dataclasses.field(default=[])
    errors:   List[str] = dataclasses.field(default=[])
    exe_path: str = None
    build: Build = None

