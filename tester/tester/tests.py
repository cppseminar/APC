from tester.config import Config
import logging
import tempfile
import shutil
import subprocess
from enum import Enum
from typing import Final
import os, pwd
from dataclasses import dataclass


logger = logging.getLogger(__name__)

class ListTestsError(Exception):
    def __init__(self, errorcode, output, file):
        self.errorcode = errorcode
        self.output = output
        self.file = file


class TestResultStatus(str, Enum):
    SUCCESS = 'Success'
    FAILED = 'Failed'
    LEAK_SANITIZER = 'Leak sanitizer'
    ADDR_SANITIZER = 'Address sanitizer'
    DBG_CONTAINERS = 'Debug containers'


@dataclass
class TestResult:
    returncode: int
    stdout: str
    stderr: str

    def get_status(self):
        if self.returncode > 0:
            if (self.stderr.find('In function:') != -1 
                    and self.stderr.find('Error:') != -1
                    and self.stderr.find('__debug') != -1):
                return TestResultStatus.DBG_CONTAINERS

            if self.stderr.find('ERROR: LeakSanitizer') != -1:
                return TestResultStatus.LEAK_SANITIZER

            if self.stderr.find('ERROR: AddressSanitizer') != -1:
                return TestResultStatus.ADDR_SANITIZER

            return TestResultStatus.FAILED

        return TestResultStatus.SUCCESS


class Tests:
    CATCH_EXEC_NAME: Final = 'main'
    SUBMISSION_EXEC_NAME: Final = 'submission'

    def __init__(self, binary, configuration):
        self.binary = binary
        self.configuration = configuration
        self._options = Config().get_catch2_configuration(configuration)
        self.test_cases = self._list_tests() 


    def _list_tests(self):
        logger.debug('Listing all unittest for binary "%s", with configuration "%s"', self.binary, self.configuration)

        temp_dir = tempfile.mkdtemp()
        temp = os.path.join(temp_dir, self.CATCH_EXEC_NAME)
        shutil.copy2(self.binary, temp)

        args = [temp, '--list-test-names-only', f'[{self.configuration}]']
        catch = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)

        if catch.returncode != 0 and len(catch.stderr) != 0:
            logger.error('Cannot list unittests from binary "%s" errno %d', self.binary, catch.returncode)
            stderr = (catch.stderr or b'').decode('utf-8')
            raise ListTestsError(catch.returncode, stderr, self.binary)

        stdout = catch.stdout.decode('utf-8')
        logger.debug('List of all tests returned "%s"', stdout)

        return stdout.splitlines()

    def run_test(self, test_case, submission_binary = None):
        logger.info('Running test "%s" in configuration %s for binary "%s"', test_case, self.configuration, submission_binary)

        temp_dir = tempfile.mkdtemp()
        logger.debug('Using folder "%s"', temp_dir)

        catch_path = os.path.join(temp_dir, self.CATCH_EXEC_NAME)
        shutil.copy2(self.binary, catch_path)

        os.chmod(temp_dir, 0o777) # everyone os allowed to do everything
        os.chmod(catch_path, 0o777) 

        pw_record = pwd.getpwnam("apc-test")
        user_uid = pw_record.pw_uid
        user_gid = pw_record.pw_gid

        env = {}
        if submission_binary:
            submission_path = os.path.join(temp_dir, self.SUBMISSION_EXEC_NAME)
            shutil.copy2(submission_binary, submission_path)
            env = { 'SUBMISSIONPATH': submission_path }

        args = [*self._options, test_case.replace(',', '\,')] # comma in test is not allowed, you need to escape it

        logger.debug('Starting tests file %s, with arguments "%s" current working directory "%s"', catch_path, ', '.join(args), temp_dir)

        def demote(user_uid, user_gid):
            os.setgid(user_gid)
            os.setuid(user_uid)

        catch = subprocess.run([catch_path, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=lambda: demote(user_uid, user_gid),
            timeout=300,
            cwd=temp_dir,
            env=env)

        stdout = catch.stdout.decode('utf-8')
        stderr = catch.stderr.decode('utf-8')

        logger.info('Test finished errno: %d', catch.returncode)
        logger.debug('Test stdout: "%s"\n stderr: "%s"', stdout, stderr)

        return TestResult(catch.returncode, stdout, stderr)