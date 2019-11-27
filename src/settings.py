"""This module will be for handling all setting in some nice way.  It should be
able to parse arguments, and later config files.  Basically you will just ask
this module for any setting you like"""

import argparse
import logging
import os

SETTINGS = None

class Settings:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Compile list of files and run tests")
        parser.add_argument('--test', help="path to the json file with test cases")
        parser.add_argument('--test-data', help="path to folder with test data", default='.')
        parser.add_argument('--output', help="path to otput directory")
        parser.add_argument('--verbose')
        parser.add_argument('paths', nargs='+', help='Files or directories to be compiled and tested.')
        args = parser.parse_args()

        self.files = self.get_files(args.paths)
        self.test_data = args.test_data
        self.test = args.test
        self.output = self.get_output_dir(args.output)
        self.verbose = args.verbose
    
    def get_files(self, paths):
        files = []
        for path in paths:
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                files += [os.path.join(path, x) for x in os.listdir(path) if x.endswith(".cpp")]
            else:
                logging.error('Object %s is not a file nor a directory.' % path)
        return files

    def get_output_dir(self, output):
        if output is None:
            import tempfile
            return tempfile.mkdtemp(prefix='students')
        else:
            return output

SETTINGS = Settings()
