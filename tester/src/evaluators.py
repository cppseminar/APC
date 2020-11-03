"""Module containing classes used for evaluation."""
import argparse
import collections
import contextlib
import csv
import dataclasses
import difflib
import itertools
import json
import operator
import os
import re



from typing import Dict, List, Any

import infrastructure
import runner

_logger = infrastructure.set_logger(__name__)


class HuffmanEvaluator(infrastructure.Module):
    """Class for evaluating huffman codes excercise."""
    SETTINGS = {
        'input_identification': infrastructure.AnyStringParser(),
        'required_size': infrastructure.AnyIntParser(),
        'source_file': infrastructure.FileNameParser(),
    }

    def __init__(self, name):
        """Register event."""
        super().__init__(name)
        self.register_event(runner.RunOutput)

    def handle_internal(self, event: runner.RunOutput):
        """Check if run output is correct."""
        if event.identification != self.settings['input_identification']:
            return False
        identification = ('[' + self.__class__.__name__ + '] ' + self.name +
                          "  -  " + event.identification + " " + event.name +
                          " " + self.name + " ")
        # First let's check if there are only required bytes
        file_bytes = self.get_byte_frequency(self.settings['source_file'])
        student_output = self.parse_output(event.output_file)
        #if (len1 := len(file_bytes)) != (len2 := len(student_output)):
        if ((set1 := set(file_bytes.keys())) !=
            (set2 := set(student_output.keys()))):
            self.notify(infrastructure.Notification(
                            message=f'{identification} Bad byte count.'
                                    f' Diff unique bytes exp {len(set1)} s {len(set2)}',
                            severity=infrastructure.MessageSeverity.ERROR,
                            payload=str(set(file_bytes.keys())
                                        ^ set(student_output.keys()))))
            # Maybe log
            return True
        # Let's check proposed file size by student implementation
        proposed_size = self._compute_expected_size(file_bytes, student_output)
        if proposed_size != int(self.settings['required_size']):
            self.notify(infrastructure.Notification(
                            message=f'{identification} file size missmatch '
                                    f'{proposed_size} != expected ( '
                                    f"{self.settings['required_size']} )",
                            severity=infrastructure.MessageSeverity.ERROR))
            return True

        self.notify(infrastructure.Notification(
                                message=f'{identification} seems valid',
                                severity=infrastructure.MessageSeverity.INFO))

        return True

    @staticmethod
    def _compute_expected_size(byte_frequency, huffman_table):
        """Given these tables, get expected file size."""
        def _compute_file_size(byte, code):
            return len(str(code)) * byte_frequency[byte]

        assert set(byte_frequency.keys()) == set(huffman_table.keys())

        expected = sum(map(lambda x: _compute_file_size(*x),
                           huffman_table.items()))
        return expected

    @staticmethod
    def get_byte_frequency(file_name) -> Dict[int, int]:
        """Return frequency map for file file_name."""
        with contextlib.suppress(FileNotFoundError):
            with open(file_name, "br") as f:
                frequency: collections.Counter = collections.Counter()
                while content := f.read(4096):
                    frequency.update(content)
                return dict(frequency)
        return {}

    @staticmethod
    def parse_output(file_name) -> Dict[int, str]:
        """Parse our expected output format.

        File must look like this:
        <byte code>: <representation>
        byte code is in range 0-255

        Example:
        0: 0
        254: 10
        255: 11
        """
        pattern = (r'^\s*'
                   r'(?P<byte>\d{1,3})'
                   r'\s*:\s*'
                   r'(?P<frequency>[01]+)'
                   r'\s*$'
                   )
        with contextlib.suppress(FileNotFoundError):
            values: Dict[int, str] = {}
            with open(file_name, "r") as file_:
                while line := file_.readline():
                    if not (match := re.match(pattern, line)):
                        return {}  # Invalid line
                    # PEP572 MYPY PR 7316, will be fixed
                    results = match.group('byte', 'frequency')  # type: ignore
                    values[int(results[0])] = str(results[1])
                return values

        return {}

class DiffEvaluator(infrastructure.Module):
    SETTINGS = {
        "expected_output": infrastructure.FileNameParser(),
        "input_identification": infrastructure.AnyStringParser(),
    }

    def __init__(self, name):
        """Register event."""
        super().__init__(name)
        self.register_event(runner.RunOutput)

    def handle_internal(self, event: runner.RunOutput):
        """Check if run output is correct."""
        if event.identification != self.settings['input_identification']:
            return False
        identificator = "[" + self.__class__.__name__ + "] " + self.name + " -"
        zipped = itertools.zip_longest(
                self.get_file_iter(self.settings["expected_output"]),
                self.get_file_iter(event.output_file),
                fillvalue="")
        for index, values in enumerate(zipped):
            if values[0] != values[1]:
                diffs = difflib.ndiff((values[0],), (values[1],))
                err = f"Line:{index+1} (starting 1)\n" +"\n".join(diffs)

                self.notify(infrastructure.Notification(
                    f"{identificator} Error wrong output",
                    infrastructure.MessageSeverity.ERROR,
                    payload=err))
                return False
        self.notify(infrastructure.Notification(f"{identificator} Correct"))

    @staticmethod
    def get_file_iter(file_name):
        try:
            with open(file_name, "r") as f:
                for line in f:
                    yield line.rstrip()
        except FileNotFoundError as error:
            _logger.info("File not found %s", file_name)
            # This will act as empty file


class OutputReplaceByFile(infrastructure.Module):
    """Reads output from file and replaces run values for input."""
    SETTINGS = {
        "filename": infrastructure.AnyStringParser(),
        "input_identificator": infrastructure.AnyStringParser(),
        "output_identificator": infrastructure.AnyStringParser(),
    }

    def __init__(self, name):
        """Register event."""
        super().__init__(name)
        self.register_event(runner.RunOutput)


    def handle_internal(self, event: runner.RunOutput):
        """Create new event, with original values, but exchange output."""
        if event.identification != self.settings['input_identificator']:
            return False
        if event.timeout:
            return False
        identificator = f"[OutputFile] {self.name}"
        # This is correct event, so let's check if output file even exists
        if not os.path.exists(self.settings["filename"]):
            self.notify(infrastructure.Notification(
                identificator + " - Output file not created",
                infrastructure.MessageSeverity.ERROR
            ))
            return False
        changes = {
            "identification": self.settings["output_identificator"],
            "output_file": self.settings["filename"]
        }
        new_event = dataclasses.replace(event, **changes)
        self.send(new_event)
        return True

class CsvSortEvaluator(infrastructure.Module):
    """Validate csv sort."""

    SETTINGS = {
        "input_identification": infrastructure.AnyStringParser(),
        "sort_indices": infrastructure.JsonListParser(),
        "required_rows": infrastructure.AnyIntParser(1),
        "required_columns": infrastructure.AnyIntParser(1),
    }

    def __init__(self, name):
        """Register event."""
        super().__init__(name)
        self.register_event(runner.RunOutput)

    @staticmethod
    def sorted_csv(csv_file: List[List[Any]], sort_columns: List[int]):
        ret = csv_file
        for column in reversed(sort_columns):
            ret = sorted(ret, key=operator.itemgetter(int(column - 1)))
        return ret

    def handle_internal(self, event: runner.RunOutput):
        """Check if file is sorted according to sort indices."""
        if event.identification != self.settings["input_identification"]:
            return False
        rows = int(self.settings["required_rows"])
        columns = int(self.settings["required_columns"])
        _temp = json.loads(self.settings["sort_indices"])
        identificator = f"[{CsvSortEvaluator.__name__}] {self.name}"
        sort_columns = []
        for column_number in _temp:
            column_number = int(column_number)
            assert column_number > 0
            assert column_number <= columns
            sort_columns.append(column_number)

        with open(event.output_file) as f:
            reader = csv.reader(f, dialect="excel")
            content = list(reader)

        # Check number of rows
        if len(content) != rows:
            self.notify(
                infrastructure.Notification(
                    message=f"{identificator} - Bad number of rows {len(content)} expected {rows}",
                    severity=infrastructure.MessageSeverity.ERROR,
                )
            )
            return False

        # Check line length
        for index, line in enumerate(content):
            if (line_len := len(line)) != columns:
                self.notify(
                    infrastructure.Notification(
                        message=f"{identificator} - Line {index+1} bad column count {line_len} expected {columns}",
                        severity=infrastructure.MessageSeverity.ERROR,
                        payload=str(line),
                    )
                )
                return False

        # Sort lines again and compare with original
        expected_content = self.sorted_csv(content, sort_columns)
        for index, lines in enumerate(zip(content, expected_content)):
            line1, line2 = lines
            if line1 != line2:
                self.notify(
                    infrastructure.Notification(
                        message=f"{identificator} - Line mismatch at line number {index+1}",
                        severity=infrastructure.MessageSeverity.ERROR,
                        payload=str(line1) + "\n" + str(line2),
                    )
                )
                return False
        self.notify(
            infrastructure.Notification(
                message=f"{identificator} - Sort correct",
                severity=infrastructure.MessageSeverity.INFO,
            )
        )
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.description = ('This script calculates expected file size '
                          'after encoded by  huffman coding.')
    parser.add_argument('-s', '--source-file', dest='binary',
                        metavar='binary_file',
                        type=argparse.FileType('r'), required=True)
    parser.add_argument('-t', '--huffman_table', dest='huffman',
                        metavar='huffman_output',
                        type=argparse.FileType('r'), required=True)
    command_line = parser.parse_args()
    huffman_file = command_line.huffman.name
    binary_file = command_line.binary.name
    command_line.huffman.close()
    command_line.binary.close()
    huffman_table = HuffmanEvaluator.parse_output(huffman_file)
    byte_table = HuffmanEvaluator.get_byte_frequency(binary_file)
    if set(huffman_table.keys()) != set(byte_table.keys()):
        print('Missmatch in bytes between files')
        exit(1)
    final_size = HuffmanEvaluator._compute_expected_size(byte_table, huffman_table)
    print(f' {final_size} is encoded file size of file {binary_file}')
    print(f' {os.path.getsize(binary_file)*8} is original size')


