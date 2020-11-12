import os
import sys
import csv
import argparse
import traceback
import json
import configparser

from typing import Iterable, Dict
from itertools import chain


import compiler
import runner
import evaluators
import infrastructure




class SimpleLogger:
    FOLDER = None

    def __init__(self, name):
        if SimpleLogger.FOLDER is None:
            import tempfile
            SimpleLogger.FOLDER = tempfile.mkdtemp(prefix='students')
        self.name = os.path.splitext(os.path.basename(name))[0] # Get filename only
        self.file = open(os.path.join(SimpleLogger.FOLDER,
                                      self.name + ".txt"),
                          "w")
        self.print(f"Logging student {os.path.basename(name)}")

    def print(self, arg, logonly=False):
        if not logonly:
            print(arg)
        self.file.write(str(arg))
        self.file.write("\n")

    def location(self):
        return f"Logs at {SimpleLogger.FOLDER}"


    def __del__(self):
        self.file.close()


def test_run(logger, compiler_, test_input, test_output, id="",
             platform=compiler.Platform.x64_Release, max_time=10, args=[], test_runs=3):

    executable = compiler_.compile(platform)
    if not executable:
        logger.print(f"Cannot run for {logger.name}, {platform.name} compilation error")
        return False
    else:
            run = compiler.TestRun(executable.file, test_input, test_output,
                                   args=args, id=logger.name + "_" + id + "_",
                                   folder=SimpleLogger.FOLDER)
            logger.print(f"Running #{id}")
            run.run(max_time=max_time, test_runs=test_runs)
            logger.print("  " + str(run))
            if not run:
                logger.print(f" Logs saved in {run.save_logs()}", logonly=True)
            # For now, always save logs
            return run

class MyModule(infrastructure.Module):
    def __init__(self, name):
        super().__init__(name)
        self.register_setting('comment', values=['ka', 'ra', 'mba'])
        self.register_setting('comment2', values=['ka', 'ra', 'mba'], default='ka')
        self.register_setting('comment3', values=[True, False], default=True)

    def handle_internal(self):
        return False



class WeirdLogger(infrastructure.Module):
    def __init__(self, name):
        super().__init__(name)
        self.register_event('compiler')

    def handle_internal(self, event):
        if event.name == 'compiler':
            print("Caught compiler event")
        return True


if __name__ == "__main__":
    script = infrastructure.TestScript()
    script.add_class(MyModule)
    script.add_class(WeirdLogger)
    script.add_class(compiler.CppFinder)
    script.add_class(compiler.Compiler)
    script.add_class(compiler.Gcc)
    script.add_class(infrastructure.HTMLWriter)
    script.add_class(infrastructure.ConsoleWriter)
    script.add_class(runner.CompilerFilter)
    script.add_class(runner.RunnerModule)
    script.add_class(runner.StdPrinter)
    script.add_class(evaluators.HuffmanEvaluator)
    script.add_class(evaluators.DiffEvaluator)
    script.add_class(evaluators.OutputReplaceByFile)
    script.add_class(evaluators.CsvSortEvaluator)
    script.add_class(evaluators.StderrCatcher)

    with open("./config.ini", "r") as f:
        script.load_ini_settings(f)

    with open("./test.ini", "w") as f:
        script.dump_ini_settings(f)

    script.add_event('start')
    script.run()
