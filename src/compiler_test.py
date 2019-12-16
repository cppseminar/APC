import compiler
import infrastructure
import pytest
import pathlib
import tempfile


class TestCompareStrings:
    def test_diff1(self):
        line1 = "aaa"
        line2 = "aab"
        assert compiler.compare_strings(line1, line2)

    def test_diff2(self):
        line1 = "aaa"
        line2 = "aaa"
        assert len(compiler.compare_strings(line1, line2)) == 0

    def test_diff3(self):
        line1 = "\n".join(("aaa", "b bc"))
        line2 = "\n".join(("aaa", "b bc\n"))
        assert len(compiler.compare_strings(line1, line2)) == 0

    def test_diff4(self):
        line1 = "\n".join(("aaa", "b bc"))
        line2 = "\n".join(("aaa", "b b c\n"))
        assert len(compiler.compare_strings(line1, line2)) != 0




@pytest.fixture
def tmp_file():
    t = tempfile.NamedTemporaryFile()
    return t.name, t


@pytest.fixture
def tmp_folder():
    t = tempfile.TemporaryDirectory()
    return t.name, t


class TestCppFinder:
    def test_invalid_settings(self, tmp_file, tmp_folder):
        finder = compiler.CppFinder('Finder')
        file_name = tmp_file[0]
        folder_name = tmp_folder[0]
        finder.set('file_path', file_name)
        finder.set('folder_path', folder_name)
        assert finder.settings
        with pytest.raises(infrastructure.ConfigError):
            finder.handle_event(infrastructure.get_valid_event('start'))

    def test_none_settings(self):
        pass
