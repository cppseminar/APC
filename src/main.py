import os
import sys
import csv
import subprocess
import traceback
import json

from typing import Iterable, Dict
from itertools import chain

import compiler
import settings

SETTINGS = settings.SETTINGS

def get_vs_vars(build_type) -> Dict[str, str]:
    """Find and call vcvarsall and return environment set by this script"""
    params = [
        "cmd",
        "/c",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Professional\\VC\\Auxiliary\\Build\\vcvarsall.bat"
        + " x64" + " & " + " set ",
    ]
    process = subprocess.run(params, capture_output=True, text=True)
    return compiler.parse_env(process.stdout)


class SimpleLogger:
    FOLDER = None

    def __init__(self, name):
        self.name = os.path.splitext(os.path.basename(name))[0]  # Get filename only
        self.file = open(os.path.join(SETTINGS.output, self.name + ".txt"), "w")
        self.print(f"Logging student {os.path.basename(name)}")

    def print(self, arg, logonly=False):
        if not logonly:
            print(arg)
        self.file.write(str(arg))
        self.file.write("\n")

    def location(self):
        return SETTINGS.output

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


if __name__ == "__main__":
    test_cases = None

    # cvs header for build summary
    header = ["Name", "Build status", "Errors", "Warnings"]

    if SETTINGS.test:
        if SETTINGS.test == 'sudoku':
            with open('test-data/sudoku.json', 'r') as f:
                test_cases = json.load(f) 

        if SETTINGS.test == 'search-substring':
            with open('test-data/search_substring.json', 'r') as f:
                test_cases = json.load(f) 

        # For each test case add 2 columns Test# and Time
        header += list(chain.from_iterable(zip(["Test" + str(i) for i in range(len(test_cases))], 
                                            ["Time" for _ in range(len(test_cases))])))

    data = []

    global_logger = SimpleLogger("Current run")

    files = SETTINGS.files if not SETTINGS.dir else [os.path.join(SETTINGS.files[0], x) for x in os.listdir(SETTINGS.files[0]) if x.endswith(".cpp")]

    for source in files:
        assert os.path.exists(source)

        builds_num = 0
        logger = SimpleLogger(str(source))
        name = logger.name
        global_logger.print(f"Student {logger.name}", logonly=True)
        c = compiler.Compiler(source, identificator=logger.name, folder=SimpleLogger.FOLDER)
        # Compile for all configs
        errors, warnings = 0, 0
        for platform_ in compiler.Platform:
            logger.print(f"Compiling platform {platform_.name}")
            executable = c.compile(platform_)

            errors += len(executable.errors)
            warnings += len(executable.warnings)

            logger.print(str(executable))
            if executable and not executable.warnings:
                builds_num += 1
            else:
                logger.print(executable.get_log(), logonly=True)

        global_logger.print(f"Successful builds {builds_num}")

        build_status = "OK" if errors + warnings == 0 else "WARNINGS" if errors == 0 else "ERRORS"
        data.append([name, build_status, errors, warnings])

        if SETTINGS.test:
            assert test_cases

            if SETTINGS.test == 'sudoku':
                for idx, test_case in enumerate(test_cases):
                    input_file = os.path.join(SETTINGS.test_data, test_case["input"])
                    output_file = os.path.join(SETTINGS.test_data, test_case["output"])

                    runs_num = 0
                    if test_run(logger, c, input_file, output_file, args=["-i", input_file], id=str(idx) + "D", platform=compiler.Platform.x64_Debug, max_time=10, test_runs=1):
                        runs_num += 1
                    current_run = test_run(logger, c, input_file, output_file, args=[
                                            "-i", input_file], id=str(idx) + "R", platform=compiler.Platform.x64_Release, max_time=100, test_runs=3)
                    if current_run:
                        runs_num += 1

                    data[-1].append(runs_num)
                    run_time = current_run.run_time if current_run else 0
                    data[-1].append(run_time)

                    global_logger.print(f"Successful runs: {runs_num}\n\n", logonly=True)
            elif SETTINGS.test == 'search-substring':
                for idx, test_case in enumerate(test_cases):
                    input_file = os.path.join(SETTINGS.test_data, test_case["input"])
                    output_file = os.path.join(SETTINGS.test_data, test_case["output"])
                    to_search = test_case["search"]

                    runs_num = 0
                    if test_run(logger, c, input_file, output_file, args=[input_file, to_search], id=str(idx) + "D", platform=compiler.Platform.x64_Debug, max_time=10, test_runs=1):
                        runs_num += 1
                    current_run = test_run(logger, c, input_file, output_file, args=[input_file, to_search], id=str(idx) + "R", platform=compiler.Platform.x64_Release, max_time=100, test_runs=3)
                    if current_run:
                        runs_num += 1

                    data[-1].append(runs_num)
                    run_time = current_run.run_time if current_run else 0
                    data[-1].append(run_time)

                    global_logger.print(f"Successful runs: {runs_num}\n\n", logonly=True)                

    # create CSV file from summary data
    with open(os.path.join(SETTINGS.output, 'builds.csv'), mode='a', newline='') as summary_file:
        build_writer = csv.writer(summary_file, delimiter=',')

        build_writer.writerow(header)

        for x in data:
            assert len(header) == len(x)
            build_writer.writerow(x)

    print(f"Logs location: { global_logger.location( )}")
