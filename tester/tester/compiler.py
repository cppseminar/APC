from dataclasses import dataclass
import logging
import subprocess
import os
import errno

from tester.timeout import TimeoutManager

logger = logging.getLogger(__name__)

@dataclass
class CompilationResult: # this is for successful compilation
    errno: int
    output_path: str
    compiler_output: str # warnings etc.

def check_cmake():
    try:
        logger.debug('Running cmake to obtain version')

        cmake = subprocess.run(['cmake', '--version'], stdout=subprocess.PIPE, timeout=5)
        if cmake.returncode != 0:
            logger.critical('cmake returned %s.', cmake.returncode)
            raise RuntimeError('cmake do not work correctly!')

        logger.debug('Running cmake version %s', cmake.stdout.decode('utf-8').split('\n')[0])

    except FileNotFoundError:
        logger.critical('cmake not found!')
        raise

    except subprocess.TimeoutExpired:
        logger.critical('cmake cannot print version in less than 5 seconds!')
        raise

def compile_cmake_project(folder):
    logger.info('Attempting to run cmake --build on folder %s', folder)

    try:
        with TimeoutManager() as timeout:
            cmake = subprocess.run(['cmake', '--build', folder, '-j', '2'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)

            if cmake.returncode != 0:
                logger.warn('Cannot compile files, check out logs at output')
                return CompilationResult(cmake.returncode, '', cmake.stdout.decode('utf-8'))
            else:
                logger.info('Project successfuly compiled and linked')
                stdout = cmake.stdout.decode('utf-8')
                # this is not pretty, but the last line of cmake is the binary,
                # so we will use that in case everything went OK
                binary = os.path.join(folder, stdout.split()[-1])
                return CompilationResult(cmake.returncode, binary, stdout)


    except subprocess.TimeoutExpired:
        logger.fatal('cmake cannot compile/link files in less than timeout provided by docker!')
        return CompilationResult(errno.ETIME, '', 'cmake reach timeout.')

def compile_cmake_lists(folder, configuration):
    logger.info('Attempting to run cmake on folder %s', folder)

    try:
        with TimeoutManager() as timeout:
            build_folder = './build-' + configuration

            cmake = subprocess.run(['cmake', '-B', build_folder, '-S', '.', '-DCMAKE_BUILD_TYPE=' + configuration], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, cwd=folder)

            if cmake.returncode != 0:
                logger.warn('Cannot create make files')
                return CompilationResult(cmake.returncode, '', cmake.stdout.decode('utf-8'))
            else:
                logger.info('Make files successfully created')
                return CompilationResult(cmake.returncode, os.path.join(folder, build_folder), cmake.stdout.decode('utf-8'))



    except subprocess.TimeoutExpired as e:
        logger.fatal('cmake cannot compile/link files in less than timeout provided by docker!')
        return CompilationResult(errno.ETIME, '', 'cmake reach timeout.')
