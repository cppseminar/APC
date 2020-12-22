"""Module containing tests for library module."""

import contextlib
import io
import pathlib
import tempfile
import os
import unittest.mock

import pytest

import library

# pylint: disable=no-self-use

# Those fixtures ...
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name

###############################
#        # FIXTURES #         #
###############################


@pytest.fixture
def patch_gtf(monkeypatch):
    """Act as if this is first instantiation of class GlobalTmpFolder."""
    monkeypatch.setattr(library.GlobalTmpFolder, '_NAME', None)
    monkeypatch.setattr(library.GlobalTmpFolder, '_FIRST_ARGS', None)
    monkeypatch.setattr(library.GlobalTmpFolder, '_DELETER', None)

###############################
#      # END FIXTURES #       #
###############################


def test_build_file_regex():
    """Check matching of file regex."""
    regex = library.build_file_regex("*.py")
    assert regex.fullmatch("file1.py")
    assert regex.fullmatch("fi le1 .py")
    assert regex.fullmatch(" fi le1_.py")
    assert not regex.fullmatch(" fi le1_.py ")
    assert not regex.fullmatch("file1py")

    regex = library.build_file_regex("*py")
    assert regex.fullmatch("file1.py")
    assert regex.fullmatch("fi le1 py")
    assert regex.fullmatch(" fi le1_py")

    regex = library.build_file_regex("*py*")
    assert regex.fullmatch("file1.py")
    assert regex.fullmatch("fi le1 py ")
    assert regex.fullmatch("python")
    assert not regex.fullmatch("pyth/on")


@contextlib.contextmanager
def tmp_dirs(levels=1, files=1):
    """Create directory structure in temp with depth=LEVELS and FILES count.

    Returns tuple of directory name and list of all file names created in
    this directory, or even subdirectories
    """
    directories = []
    created_files = []
    main_dir = tempfile.TemporaryDirectory(prefix='dir')
    directory = main_dir.name
    try:
        for _ in range(levels):
            directories.append(
                tempfile.TemporaryDirectory(prefix='dir', dir=directory))
            directories.append(
                tempfile.TemporaryDirectory(prefix='dir', dir=directory))
            for _ in range(files):
                file_1 = tempfile.NamedTemporaryFile(dir=directories[-1].name,
                                                     delete=False)
                file_2 = tempfile.NamedTemporaryFile(dir=directories[-2].name,
                                                     delete=False)
                created_files.append(file_1)
                created_files.append(file_2)

            # Make also second level
            directory = directories[-1].name

        file_names = list(map(lambda x: pathlib.Path(x.name), created_files))
        directory_names = list(map(lambda x: pathlib.Path(x.name),
                                   directories))

        yield pathlib.Path(main_dir.name), file_names, directory_names
    finally:
        for file_ in created_files:
            file_.close()


def test_iterate_files():
    """Test whether all created files are returned by iterator."""
    with tmp_dirs(levels=1) as (directory, files, dirs):
        files2 = library.iterate_files(directory, include_dirs=False)
        assert (set(files)) == set(files2)
        files_and_dirs = library.iterate_files(directory, include_dirs=True)
        assert set(files_and_dirs) == set(files) | set(dirs)
        assert list(library.iterate_files(
            tempfile.TemporaryDirectory().name)) == []


def test_filter_files():
    """Test whether wildcards are matching properly."""
    with tmp_dirs(levels=1) as (directory, files, _):
        files2 = library.iterate_files(directory, include_dirs=False)
        assert set(library.filter_files(files2, wildcard='*')) == set(files)
    path1 = pathlib.PurePath('/home/asdf/file1 .py')
    path2 = pathlib.Path(__file__)
    path3 = 'C:\\asd.py'
    path4 = "file2.py"
    array = [path1, path2, path3, path4]
    assert array == list(library.filter_files(array, "*.py"))
    assert array == list(library.filter_files(array, "*py"))
    assert [] == list(library.filter_files(array, "*.cpp"))
    assert array == list(
        library.filter_files(array + ["filepy", "file.cpp"], "*.py"))


def test_str_to_valid_file_name():
    """Test for str to valid file name."""
    func = library.str_to_valid_file_name
    assert func('file.exe') == 'file.exe'
    assert func('file/.exe') == 'file.exe'
    assert func('<>:"/|\\/?*') == ''
    assert func('file .e xe  ') == 'file .e xe'


class TestGlobalTmpFolder:
    """Test behavior of GlobalTmpFolder."""

    def test_creation(self, patch_gtf):
        """Test whether class behaves properly.

        Check if name member is accessible and if class is convertible to str.
        Also check whether both objects returned same folder.
        """
        global1 = library.GlobalTmpFolder()
        global2 = library.GlobalTmpFolder()
        assert global1.name == global2.name
        assert str(global1) == global1.name
        with pytest.raises(ValueError):
            library.GlobalTmpFolder(prefix="a")

    def test_arguments(self, patch_gtf):
        """Test whether mkdtemp is called with proper args.

        Important also for order of args.
        """
        mock_mkdtemp = unittest.mock.MagicMock(return_value=tempfile.mkdtemp())
        with unittest.mock.patch('tempfile.mkdtemp', new=mock_mkdtemp):
            library.GlobalTmpFolder(prefix='asf', suffix='123', directory='aa')
            mock_mkdtemp.assert_called_once_with('123', 'asf', 'aa')
        # Let's try to do cleanup
        with contextlib.suppress(OSError):
            os.rmdir(mock_mkdtemp())

    def test_cleanup_empty(self, patch_gtf):
        """Test whether cleanup works properly."""
        global1 = library.GlobalTmpFolder()
        folder = global1.name
        del global1
        del library.GlobalTmpFolder._DELETER
        assert not os.path.exists(folder)

    def test_cleanup_non_empty(self, patch_gtf):
        """Test whether cleanup works properly."""
        global1 = library.GlobalTmpFolder()
        folder = global1.name
        tmp_file = tempfile.NamedTemporaryFile(dir=folder, suffix='.py')
        del global1
        del library.GlobalTmpFolder._DELETER
        assert os.path.exists(folder)
        del tmp_file
        os.rmdir(folder)

    def test_access_after_deletion(self, patch_gtf):
        """Folder cannot be deleted before last instance."""
        global1 = library.GlobalTmpFolder()
        global2 = library.GlobalTmpFolder()
        folder = global1.name
        del global1
        assert os.path.exists(folder)
        del global2
        assert os.path.exists(folder)
        del library.GlobalTmpFolder._DELETER
        assert not os.path.exists(folder)

class TestBinaryDiff:
    def test_empty(self):
        stream1 = io.BytesIO(bytes())
        stream2 = io.BytesIO(bytes())
        result, _ = library.binary_diff(stream1, stream2)
        assert result == True

    def test_unequal_size(self):
        stream1 = io.BytesIO(b"ahoj ako sa mas")
        stream2 = io.BytesIO(b"ahoj mam sa dobre")
        result, _ = library.binary_diff(stream1, stream2)
        assert result == False

    def test_unequal(self):
        stream1 = io.BytesIO(b"ahoj mas sa dobre?")
        stream2 = io.BytesIO(b"ahoj mam sa dobre!")
        result, message = library.binary_diff(stream1, stream2)
        assert message == "6a | 20 | 6d | 61 | 73!=6d on position 8"
        assert result == False

    def test_equal(self):
        stream1 = io.BytesIO(b"ahoj mam sa dobre!")
        stream2 = io.BytesIO(b"ahoj mam sa dobre!")
        result, _ = library.binary_diff(stream1, stream2)
        assert result == True
