"""Module containing classes used for evaluation."""
import argparse
import collections
import contextlib
import functools
import os
import re

from typing import Dict

import infrastructure
import runner


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
        identification = (event.identification + " " + event.name + " "
                          + self.name + " " + self.__class__.__name__ + " ")
        # First let's check if there are only required bytes
        file_bytes = self.get_byte_frequency(self.settings['source_file'])
        student_output = self.parse_output(event.output_file)
        if (len1 := len(file_bytes)) != (len2 := len(student_output)):
            self.notify(infrastructure.Notification(
                            message=f'Bad byte count for {identification}.'
                                    f' Diff unique bytes {len1} {len2}',
                            severity=infrastructure.MessageSeverity.ERROR,
                            payload=str(set(file_bytes.keys())
                                        - set(student_output.keys()))))
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
                content = f.read()
                frequency: Dict[int, int] = collections.defaultdict(lambda: 0)
                for byte in content:
                    index = int(byte)
                    frequency[index] = frequency[index] + 1
                return frequency
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
            values: Dict[int, int] = {}
            with open(file_name, "r") as file_:
                while line := file_.readline():
                    if not (match := re.match(pattern, line)):
                        return {}  # Invalid line
                    # PEP572 MYPY PR 7316, will be fixed
                    results = match.group('byte', 'frequency')  # type: ignore
                    values[int(results[0])] = str(results[1])
                return values

        return {}

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


