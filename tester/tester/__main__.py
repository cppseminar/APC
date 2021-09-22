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
        'compilation': [{
            'binary': binary,
            'configurations': [{
                'name': name,
                'result': result
            } for name, result in configurations.items()]
        } for binary, configurations in binaries.items()],
        'tests': [{
            'configuration': configuration, 
            'cases': [{
                'name': name, 
                'result': result
            } for name, result in cases.items()]
        } for configuration, cases in tests_result.items()]
    }

    with open(Config.teachers_json(), 'w') as f:
        json.dump(teachers, f, cls=EnhancedJSONEncoder, indent=4)

    students = {
        'compilation': [{
            'binary': binary,
            'configurations': [{
                'name': name,
                'result': result.compiler_output if Config.get_visibility(name, Visibility.BUILD) else '' 
            } for name, result in configurations.items()]
        } for binary, configurations in binaries.items()],
        'tests': [{
            'configuration': configuration, 
            'cases': [{
                'name': name,
                'status': result.get_status() == tester.tests.TestResultStatus.SUCCESS,
                'result': result.stdout if Config.get_visibility(configuration, Visibility.TESTS) else ''
            } for name, result in cases.items()]
        } for configuration, cases in tests_result.items()]
    }

    with open(Config.students_json(), 'w') as f:
        json.dump(students, f, cls=EnhancedJSONEncoder, indent=4)

def main():
    """
    Main entry point of our python tester. It will first of all
    load settings, compile sources, run tests and collect results, 
    then it will pack those and send everything to output folder.
    """
    # start logger
    tester.logger.configure()
    logger.info('Tester started...')
    logger.debug(Config.dumps())


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
        if binary.errno != 0:
            continue # build failed

        test_results[configuration] = {}
        tests = tester.tests.Tests(binary.output_path, configuration)
        for test_case in tests.test_cases:
            submission_binary = binaries.get('submission', {}).get(configuration, None)
            if submission_binary and submission_binary.errno != 0:
                continue # cannot compile submission

            test_result = tests.run_test(test_case, submission_binary.output_path)
            test_results[configuration][test_case] = test_result

    create_success_output(binaries, test_results)

    logger.info('Finished.')


if __name__ == '__main__':
    main()