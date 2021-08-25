import logging
import os
import shutil
import dataclasses
import json
import tempfile

from tester.config import Config, SubmissionMode, Visibility
import tester.logger
import tester.compiler as compiler
import tester.tests

logger = logging.getLogger(__name__)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, tester.tests.TestResult):
            return {
                'status': o.get_status(), 
                **dataclasses.asdict(o)
            }
        elif dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        else:
            return super().default(o)

def create_build_errors(error):
    logger.debug('Creating json with build errors')

    teachers = {
        'status': f'Compilation of {error.file} failed.',
        'configuration': error.configuration,
        'error_code': error.errorcode,
        'description': error.description,
        'text': error.compiler_output,
    }

    with open(Config.teachers_json(), 'w') as f:
        json.dump(teachers, f)

    students = {
        'status': 'Compilation of failed.',
        'configuration': error.configuration,
        'description': error.description,
        'text': 
            error.compiler_output 
            if Config.get_visibility(error.configuration, Visibility.BUILD) 
            else ''
    }

    with open(Config.students_json(), 'w') as f:
        json.dump(students, f)


def create_list_tests_errors(error):
    logger.debug('Creating json with errors')

    teachers = {
        'status': f'Listing of tests from file {error.file} failed.',
        'error_code': error.errorcode,
        'text': error.output,
    }

    with open(Config.teachers_json(), 'w') as f:
        json.dump(teachers, f)

    students = {
        'status': f'Listing of tests from file {error.file} failed.',
        'text': 'This is most likely because you did something wrong in global initializers. If you believe it is not the case, contact us.',
    }

    with open(Config.students_json(), 'w') as f:
        json.dump(students, f)


def build(out_dir, in_dir):
    build_path = os.path.join(Config.output_path(), out_dir)

    # we need to create the build directory
    os.makedirs(build_path, exist_ok=True)

    binaries = {}

    for configuration in Config.get_configurations():
        dir = os.path.join(build_path, configuration)
        os.mkdir(dir)

        comp = compiler.GccCompiler(configuration, dir)

        binaries[configuration] = comp.compile(in_dir)

    return binaries


def create_success_output(binaries, tests_result):
    logger.debug('Creating json with tests results')

    teachers = {
        'compilation': binaries,
        'tests': tests_result
    }

    with open(Config.teachers_json(), 'w') as f:
        json.dump(teachers, f, cls=EnhancedJSONEncoder, indent=4)

    def strip_info_for_students(d):
        return {
            'compilation': {
                name: {
                    configuration: 
                        result.compiler_output 
                        if Config.get_visibility(configuration, Visibility.BUILD) 
                        else '' 
                    for configuration, result in binary.items()
                } for name, binary in d['compilation'].items()
            },
            'tests': {
                configuration: {
                    case:
                        result.stdout 
                        if Config.get_visibility(configuration, Visibility.TESTS) 
                        else (
                            'Success' 
                            if result.get_status() == tester.tests.TestResultStatus.SUCCESS 
                            else 'Failed'
                        )
                    for case, result in results.items()
                } for configuration, results in d['tests'].items()
            }       
        }

    students = strip_info_for_students(teachers)

    with open(Config.students_json(), 'w') as f:
        json.dump(students, f, cls=EnhancedJSONEncoder, indent=4)

def main():
    """
    Main entry point of our python tester. It will first of all
    load settings, compile sources, run tests and collect results, 
    then it will pack those and send everything to output folder.
    """
    # clear output directory
    if os.path.exists(Config.output_path()) != 0:
        shutil.rmtree(Config.output_path())

    # start logger
    tester.logger.configure()
    logger.info('Tester started...')
    logger.info(Config.dumps())

    try:
        test_results = {}

        # prepare folder to build tests
        tests_dir = tempfile.mkdtemp()
        shutil.copytree(Config.tests_path(), tests_dir, dirs_exist_ok=True)
    
        if Config.get_mode() == SubmissionMode.COPY:
            shutil.copy2(Config.submission_path(), tests_dir)

        logger.debug('Copied files for build to "%s"', tests_dir)

        binaries = { 'tests': build('tests', tests_dir) }

        if Config.get_mode() == SubmissionMode.BUILD:
            binaries['submission'] = build('submission', Config.submission_path())

        for configuration, binary in binaries['tests'].items():
            test_results[configuration] = {}
            tests = tester.tests.Tests(binary.output_path, configuration)
            for test_case in tests.test_cases:
                test_result = tests.run_test(test_case, binaries['submission'][configuration].output_path)
                test_results[configuration][test_case] = test_result

        create_success_output(binaries, test_results)

        logger.debug('Finished.')

    except tester.compiler.CompilationError as e:
        create_build_errors(e)
    except tester.tests.ListTestsError as e:
        create_list_tests_errors(e)


if __name__ == '__main__':
    main()