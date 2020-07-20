import compiler
import infrastructure
import pytest
import tempfile


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




