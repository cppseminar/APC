import pprint
import os
import enum


class SubmissionMode(enum.Enum):
    COPY = 'copy'
    BUILD = 'build'

class Configuration(str, enum.Enum):
    DEBUG = 'debug'
    RELEASE = 'release'

    def __str__(self):
        return str(self.value)

class Config:
    @classmethod
    def dumps(cls):
        pp = pprint.PrettyPrinter(indent=4, compact=False)
        s = pp.pformat(os.environ)
        return f'Current env: \n {s}'

    @classmethod
    def output_path(cls):
        dir = os.getenv('OUTPUT_PATH')

        if not os.path.exists(dir):
            os.mkdir(dir)

        return dir

    @classmethod
    def show_results_to_students(cls):
        return os.getenv('SHOW_RESULTS_TO_STUDENTS', '0') == '1'
        
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
        mode = os.getenv('TEST_MODE', '')
        if mode == 'build':
            return SubmissionMode.BUILD
        elif mode == 'copy':
            return SubmissionMode.COPY

        raise RuntimeError('mode not specified')
