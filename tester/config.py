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
_parser.add_argument('conf_path', help='Path to ini file with appropriate confuguration')
_parser.add_argument('-C', '--configuration', help='Run just one configuration, without it will run all')
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
    def get_configurations(cls):
        if _args.configuration:
            return [_args.configuration]
        
        return list(dict.fromkeys([
            *cls._SETTINGS['compiler'].keys(),
            *cls._SETTINGS['linker'].keys(),
        ]))

    @classmethod
    def get_compiler_settings(cls, configuration):
        return shlex.split(cls._SETTINGS['compiler'].get(configuration, '').strip('"'))

    @classmethod
    def get_linker_settings(cls, configuration):
        return shlex.split(cls._SETTINGS['linker'].get(configuration, '').strip('"'))

    @classmethod
    def get_visibility(cls, configuration: str, visibility: Visibility):
        data = cls._SETTINGS['visibility']

        if not configuration in data:
            return False

        return data[configuration].find(visibility.value) != -1


    @classmethod
    def get_catch2_configurations(cls):
        catch2 = cls._SETTINGS['tests']

        result = { 
            key: shlex.split(value.strip('"')) for (key, value) in catch2.items() 
        }

        return result

    @classmethod
    def output_path(cls):
        dir = cls._SETTINGS['paths']['output']

        if not os.path.exists(dir):
            os.mkdir(dir)

        return dir

    @classmethod
    def submission_path(cls):
        return cls._SETTINGS['paths']['submission']

    @classmethod
    def compiler_path(cls):
        return cls._SETTINGS['paths']['compiler']

    @classmethod
    def tests_path(cls):
        return cls._SETTINGS['paths']['tests']

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