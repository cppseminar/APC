"""This script is very interconnected with Dockerfile and paths there
be sure to check the file if you plan to change something.
"""

import logging
import os
import shutil
import dataclasses
import json

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

def build(project_path):
    build_result = compiler.compile_cmake_project(project_path)

    build_output = os.path.join(Config.build_output_path(), project_path.replace('/', '_') + '.txt')

    with open(build_output, "w") as text_file:
        text_file.write(build_result.compiler_output)

    return build_result

def build_tests():
    # copy submission to main test file
    if Config.get_mode() == SubmissionMode.COPY:
        # this is quite a hack, input file is always named main.cpp, so
        # we need to change that to header file
        shutil.copy2(os.path.join(Config.submission_path(), 'main.cpp'), os.path.join(Config.tests_path(), 'submission.h'))

    result = {}
    for configuration in ['debug', 'release']:
        result[configuration] = build(os.path.join(Config.tests_path(), 'build-' + configuration))

    return result

def build_submission():
    if Config.get_mode() != SubmissionMode.BUILD:
        return {}

    shutil.copy2(os.path.join(Config.submission_path(), 'main.cpp'), Config.submission_project())

    result = {}
    for configuration in ['debug', 'release']:
        project_result = compiler.compile_cmake_lists(Config.submission_project(), configuration)

        build_output = os.path.join(Config.build_output_path(), Config.submission_project().replace('/', '_') + '-' + configuration + '-cmake-lists.txt')

        with open(build_output, "w") as text_file:
            text_file.write(project_result.compiler_output)

        if project_result.errno != 0:
            return {}

        result[configuration] = build(project_result.output_path)

    return result

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

    compiler.check_cmake()

    test_results = {}

    binaries = { 'tests': build_tests() }

    if Config.get_mode() == SubmissionMode.BUILD:
        binaries['submission'] = build_submission()

    for configuration, binary in binaries['tests'].items():
        if binary.errno != 0:
            continue # build failed

        test_results[configuration] = {}
        tests = tester.tests.Tests(binary.output_path, configuration)
        for test_case in tests.test_cases:
            submission_binary = binaries.get('submission', {}).get(configuration, None)
            if submission_binary:
                if submission_binary.errno != 0:
                    continue # cannot compile submission

                test_result = tests.run_test(test_case, submission_binary.output_path)
            else:
                test_result = tests.run_test(test_case)
            test_results[configuration][test_case] = test_result

    create_success_output(binaries, test_results)

    logger.info('Finished.')


if __name__ == '__main__':
    main()
