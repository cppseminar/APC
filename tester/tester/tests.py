import logging
import tempfile
import shutil
import subprocess
from enum import Enum
from typing import Final
import os, pwd
from dataclasses import dataclass

from tester.timeout import TimeoutManager
from tester.config import Config, Configuration, SubmissionMode

logger = logging.getLogger(__name__)

class ListTestsError(Exception):
    def __init__(self, errorcode, output, file):
        self.errorcode = errorcode
        self.output = output
        self.file = file


class TestResultStatus(str, Enum):
    SUCCESS = 'Success'
    FAILED = 'Failed'
    TIMEOUT = 'Timeout'
    LEAK_SANITIZER = 'Leak sanitizer'
    ADDR_SANITIZER = 'Address sanitizer'
    DBG_CONTAINERS = 'Debug containers'


@dataclass
class TestResult:
    returncode: int
    stdout: str
    stderr: str

    def get_status(self):
        if self.returncode == -2147483649:
            return TestResultStatus.TIMEOUT

        is_dbg_container = lambda x: (x.find('In function:') != -1
            and x.find('Error:') != -1 and x.find('__debug') != -1)

        if self.returncode != 0:
            if self.stderr.find('ERROR: LeakSanitizer') != -1:
                return TestResultStatus.LEAK_SANITIZER

            if self.stderr.find('ERROR: AddressSanitizer') != -1:
                return TestResultStatus.ADDR_SANITIZER

            if (is_dbg_container(self.stderr)):
                return TestResultStatus.DBG_CONTAINERS

            return TestResultStatus.FAILED

        if (is_dbg_container(self.stderr)):
            return TestResultStatus.DBG_CONTAINERS

        return TestResultStatus.SUCCESS


class Tests:
    CATCH_EXEC_NAME: Final = 'main'
    SUBMISSION_EXEC_NAME: Final = 'submission'

    def __init__(self, binary, configuration):
        self.binary = binary
        self.configuration = configuration
        self._options = ['--durations', 'yes', '--invisibles']
        if self.configuration == Configuration.DEBUG:
            self._options.append('--success')
        self.test_cases = self._list_tests()


    def _list_tests(self):
        logger.debug('Listing all unittest for binary "%s", with configuration "%s"', self.binary, str(self.configuration))

        temp_dir = tempfile.mkdtemp()
        temp = os.path.join(temp_dir, self.CATCH_EXEC_NAME)
        shutil.copy2(self.binary, temp)

        args = [temp, '--list-tests', '--verbosity', 'quiet', f'[{self.configuration}]']
        catch = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)

        if catch.returncode != 0 and len(catch.stderr) != 0:
            logger.error('Cannot list unittests from binary "%s" errno %d', self.binary, catch.returncode)
            stderr = (catch.stderr or b'').decode('utf-8')
            raise ListTestsError(catch.returncode, stderr, self.binary)

        stdout = catch.stdout.decode('utf-8')
        logger.debug('List of all tests returned "%s"', stdout)

        return stdout.splitlines()

    def run_test(self, test_case, submission_binary = None):
        logger.info('Running test "%s" in configuration "%s".', test_case, str(self.configuration))

        temp_dir = tempfile.mkdtemp()
        logger.debug('Using folder "%s"', temp_dir)

        catch_path = os.path.join(temp_dir, self.CATCH_EXEC_NAME)
        shutil.copy2(self.binary, catch_path)

        os.chmod(temp_dir, 0o777) # everyone os allowed to do everything
        os.chmod(catch_path, 0o777)

        pw_record = pwd.getpwnam("apc-test")
        user_uid = pw_record.pw_uid
        user_gid = pw_record.pw_gid

        env = {
            'DATAPATH': Config.data_path(),
        }
        if submission_binary:
            submission_path = os.path.join(temp_dir, self.SUBMISSION_EXEC_NAME)
            shutil.copy2(submission_binary, submission_path)
            env['SUBMISSIONPATH'] = submission_path

        args = [*self._options, test_case.replace(',', '\,')] # comma in test is not allowed, you need to escape it

        logger.debug('Starting tests file %s, with arguments "%s" current working directory "%s"', catch_path, ', '.join(args), temp_dir)

        def demote(user_uid, user_gid):
            os.setgid(user_gid)
            os.setuid(user_uid)

        with TimeoutManager() as timeout:
            try:
                catch = subprocess.run([catch_path, *args],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=lambda: demote(user_uid, user_gid),
                    timeout=timeout if Config.get_mode() == SubmissionMode.BUILD else min(timeout, 180),
                    cwd=temp_dir,
                    env=env)

                stdout = catch.stdout.decode('raw_unicode_escape')
                stderr = catch.stderr.decode('raw_unicode_escape')

                logger.info('Test finished errno: %d', catch.returncode)
                logger.debug('Test stdout: "%s"\n stderr: "%s"', stdout, stderr)

                return TestResult(catch.returncode, stdout, stderr)
            except subprocess.TimeoutExpired:
                logger.info('Test timeouted.')
                # first negative number that cannot be represented with 32 bit signed int (assuming 2-complement)
                return TestResult(-2147483649, '', 'Subprocess timeout expired!')
