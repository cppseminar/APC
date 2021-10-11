from dataclasses import dataclass
import logging
import subprocess
import os
import errno

from tester.config import Config

logger = logging.getLogger(__name__)

@dataclass
class CompilationResult: # this is for successful compilation
    errno: int
    output_path: str
    compiler_output: str # warnings etc.

class GccCompiler:
    def __init__(self, configuration, output_path):
        logger.info('Creating compiler class with configuration %s output path is "%s"', configuration, output_path)

        self._compiler_options = Config.get_compiler_settings(configuration)
        self._linker_options = Config.get_linker_settings(configuration)
        self._output_path = output_path
        self._gcc_path = Config.compiler_path()
        
        try:
            logger.debug('Running Gcc ("%s") to obtain version', self._gcc_path)
            
            gcc = subprocess.run([self._gcc_path, '--version'], stdout=subprocess.PIPE, timeout=5)
            if gcc.returncode != 0:
                logger.critical('Gcc returned %s.', gcc.returncode)
                raise RuntimeError('Gcc do not work correctly!')

            logger.debug('Running Gcc version %s', gcc.stdout.decode('utf-8').split('\n')[0])

        except FileNotFoundError:
            logger.critical('Gcc not found!')
            raise

        except subprocess.TimeoutExpired:
            logger.critical('Gcc cannot print version in less than 5 seconds!')
            raise


    def _compile_files(self, paths):
        compile_log = os.path.join(self._output_path, 'compile-stdout.log')
        compile_output = b''

        try:
            obj_path = os.path.join(self._output_path, 'obj')
            os.mkdir(obj_path)

            logger.debug('Created path for object files "%s".', obj_path)

            obj_files = []

            for file in paths:
                logger.debug('Examining file "%s".', file)

                obj_file = os.path.join(obj_path, os.path.basename(file) + '.o')

                if file.endswith('.cpp'):
                    args = [self._gcc_path, '-c', '-o', obj_file, '--std=c++20', *self._compiler_options, file]
                elif file.endswith('.c'):
                    args = [self._gcc_path, '-xc', '-c', '-o', obj_file, '--std=c11', *self._compiler_options, '-Wno-error=vla', '-Wno-vla', file]
                else:
                    continue # skip headers etc.

                logger.debug('Attempting to compile object file "%s".', obj_file)
                
                logger.debug('Running g++ (compile phase) with options %s', ' '.join(args))

                gcc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
                compile_output += gcc.stdout
            
                if gcc.returncode != 0:
                    logger.warn('Cannot compile file "%s", check out logs at "%s"', file, self._output_path)
                    return CompilationResult(gcc.returncode, '', gcc.stdout.decode('utf-8'))

                obj_files.append(obj_file) # add new object file to compile

            # link it together
            logger.debug('Running link phase')

            output = os.path.join(self._output_path, 'main')

            args = [self._gcc_path, '-o', output, *obj_files, *self._linker_options]
            logger.debug('Running g++ (link phase) with options %s', ' '.join(args))

            gcc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
            compile_output += gcc.stdout

            if gcc.returncode != 0:
                logger.error('Cannot link files, check out logs at "%s"', self._output_path)
                return CompilationResult(gcc.returncode, '', gcc.stdout.decode('utf-8'))
            
            logger.info('File(s) %s successfuly compiled and linked', self._output_path)
            return CompilationResult(0, output, compile_output.decode('utf-8'))

        except subprocess.TimeoutExpired as e:
            logger.fatal('Gcc cannot compile/link files in less than 300seconds!')
            return CompilationResult(errno.ETIME, '', 'Gcc reach timeout 300s.')

        finally:
            logger.debug('Writing output compilation log "%s".', compile_log)

            # create also text log with output from compilers
            with open(compile_log, 'ab') as f:
                f.write(compile_output)


    def compile(self, path):
        logger.info('Compilation for "%s" requested.', path)

        if os.path.isfile(path):
            return self._compile_files([path])
        else:
            return self._compile_files([os.path.join(path, file) for file in os.listdir(path)])
