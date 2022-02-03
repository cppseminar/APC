import configparser
import pprint
import argparse
import os
import shlex
import enum

class Visibility(enum.Enum):
    BUILD = 'build' # Output of gcc compiler is visible to students.
    TESTS = 'tests' # Output of unittest framework is visible to students.

class SubmissionMode(enum.Enum):
    COPY = 'copy'
    BUILD = 'build'

_parser = argparse.ArgumentParser()
_parser.add_argument('conf_path', help='Path to ini file with appropriate configuration')
_args = _parser.parse_args()

def _load_config(path):
    settings = configparser.ConfigParser()
    settings.read(path)
    return settings

class Config:
    _SETTINGS = _load_config(_args.conf_path)

    @classmethod
    def dumps(cls):
        config = {section: dict(cls._SETTINGS[section]) for section in cls._SETTINGS.sections()}
        pp = pprint.PrettyPrinter(indent=4, compact=False)
        s = pp.pformat(config)
        return f'Current config: \n {s}'

    @classmethod
    def get_visibility(cls, configuration: str, visibility: Visibility):
        data = cls._SETTINGS['visibility']

        if not configuration in data:
            return False

        return data[configuration].find(visibility.value) != -1


    @classmethod
    def get_catch2_configuration(cls, configuration):
        catch2 = cls._SETTINGS['tests']

        result = {
            key: shlex.split(value.strip('"')) for (key, value) in catch2.items()
        }

        return result.get(configuration, [])

    @classmethod
    def output_path(cls):
        dir = os.getenv('OUTPUT_PATH')

        if not os.path.exists(dir):
            os.mkdir(dir)

        return dir

    @classmethod
    def build_output_path(cls):
        dir = os.path.join(os.getenv('OUTPUT_PATH'), 'build')

        if not os.path.exists(dir):
            os.mkdir(dir)

        return dir

    @classmethod
    def submission_path(cls):
        return os.getenv('SUBMISSION_PATH')

    @classmethod
    def submission_project(cls):
        return os.getenv('SUBMISSION_PROJECT')

    @classmethod
    def tests_path(cls):
        return os.getenv('TESTS_PATH')

    @classmethod
    def data_path(cls):
        return os.getenv('DATA_PATH')

    @classmethod
    def teachers_json(cls):
        return os.path.join(cls.output_path(), 'teachers.json')

    @classmethod
    def students_json(cls):
        return os.path.join(cls.output_path(), 'students.json')

    @classmethod
    def get_mode(cls):
        if (cls._SETTINGS['mode'].getboolean('compile')):
            return SubmissionMode.BUILD

        return SubmissionMode.COPY
