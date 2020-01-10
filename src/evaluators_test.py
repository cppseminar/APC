"""Test for evaluators.py."""
import tempfile
import os
import weakref
import unittest.mock

import evaluators
import infrastructure
import runner

# pylint: disable=no-self-use


class TestHuffmanEvaluator:
    """Tests for huffman evaluator."""

    def test_get_byte_frequency(self):
        """Test if byte frequency is correct."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        weakref.finalize(temp_file, os.unlink, temp_file.name)
        output = evaluators.HuffmanEvaluator.get_byte_frequency('asd')
        assert output == {}
        output = evaluators.HuffmanEvaluator.get_byte_frequency(temp_file.name)
        assert output == {}
        with open(temp_file.name, "wb") as file_:
            file_.write(b'\x00\x10\x00')
        output = evaluators.HuffmanEvaluator.get_byte_frequency(temp_file.name)
        assert output == {0: 2, 16: 1}

    def test_parse_output(self):
        """Test if file loading is correct."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        weakref.finalize(temp_file, os.unlink, temp_file.name)
        # Test empty file
        output = evaluators.HuffmanEvaluator.parse_output(temp_file.name)
        assert output == {}
        # Test non existing file
        output = evaluators.HuffmanEvaluator.parse_output('asdf')
        assert output == {}
        # Test normal file
        with open(temp_file.name, "w") as file_:
            file_.write('0: 0\n')
            file_.write('2: 10\n')
            file_.write('255: 11\n')
        output = evaluators.HuffmanEvaluator.parse_output(temp_file.name)
        assert output == {0: '0', 2: '10', 255: '11'}
        # Same test but without newline at the end
        with open(temp_file.name, "w") as file_:
            file_.write('0: 0\n')
            file_.write('2: 10\n')
            file_.write('255: 11')
        output = evaluators.HuffmanEvaluator.parse_output(temp_file.name)
        assert output == {0: '0', 2: '10', 255: '11'}
        # Test file with invalid value
        with open(temp_file.name, "w") as file_:
            file_.write('0: 0\n')
            file_.write('1:23\n')
            file_.write('2: 10\n')
        output = evaluators.HuffmanEvaluator.parse_output(temp_file.name)
        assert output == {}

    def test_bad_count(self, monkeypatch):
        """Test if byte count is checked properly."""
        evaluator = evaluators.HuffmanEvaluator(name='test')
        evaluator.set('input_identification', 'a')
        evaluator.set('required_size', 5)  # BS
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        weakref.finalize(temp_file, os.unlink, temp_file.name)
        with open(temp_file.name, "w") as file_:
            file_.write('0: 0\n')
            file_.write('2: 10\n')
            file_.write('255: 11\n')
        temp_file2 = tempfile.NamedTemporaryFile(delete=False)
        temp_file2.close()
        weakref.finalize(temp_file2, os.unlink, temp_file2.name)
        evaluator.set('source_file', temp_file2.name)
        with open(temp_file2.name, "wb") as file_:
            file_.write(b'\xff\x02\00\x11')
        event = runner.RunOutput(timeout=False, identification='a',
                                 output_file=temp_file.name)
        mock = unittest.mock.MagicMock()
        monkeypatch.setattr(evaluator, 'notify', mock)
        assert evaluator.handle_event(event)
        assert mock.call_count == 1
        assert (mock.call_args[0][0].severity ==
                infrastructure.MessageSeverity.ERROR)
        # Call again, but now we expect it to be ok
        with open(temp_file2.name, "wb") as file_:
            file_.write(b'\xff\x02\00')
        assert evaluator.handle_event(event)
        assert mock.call_count == 2
        assert (mock.call_args[0][0].severity ==
                infrastructure.MessageSeverity.INFO)

    def test_correct_file_size(self, monkeypatch):
        evaluator = evaluators.HuffmanEvaluator(name='test')
        evaluator.set('input_identification', 'a')
        evaluator.set('required_size', 5)  # BS
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        weakref.finalize(temp_file, os.unlink, temp_file.name)
        with open(temp_file.name, "w") as file_:
            file_.write('0: 01\n')
            file_.write('2: 001\n')
            file_.write('255: 000\n')
        temp_file2 = tempfile.NamedTemporaryFile(delete=False)
        temp_file2.close()
        weakref.finalize(temp_file2, os.unlink, temp_file2.name)
        evaluator.set('source_file', temp_file2.name)
        with open(temp_file2.name, "wb") as file_:
            file_.write(b'\xff\x02\00\x00')
        event = runner.RunOutput(timeout=False, identification='a',
                                 output_file=temp_file.name)
        mock = unittest.mock.MagicMock()
        monkeypatch.setattr(evaluator, 'notify', mock)
        assert evaluator.handle_event(event)
        assert mock.call_count == 1
        assert (mock.call_args[0][0].severity ==
                infrastructure.MessageSeverity.ERROR)
        evaluator.set('required_size', 2*2 + 3*1 + 3*1)
        assert evaluator.handle_event(event)
        assert mock.call_count == 2
        assert (mock.call_args[0][0].severity ==
                infrastructure.MessageSeverity.INFO)

    def test_compute_size(self):
        """Test if we are calculating size properly."""
        frequency = {1: 5, 255: 3}
        table = {1 : '000', 255: '0010'}
        result = evaluators.HuffmanEvaluator._compute_expected_size(frequency,
                                                                    table)
        assert result == 5*3 + 3*4
