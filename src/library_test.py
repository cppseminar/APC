"""Module containing tests for library module"""

import contextlib
import pathlib
import tempfile

import library


def test_build_file_regex():
    f = library.build_file_regex
    r = f("*.py")
    assert r.fullmatch("file1.py")
    assert r.fullmatch("fi le1 .py")
    assert r.fullmatch(" fi le1_.py")
    assert not r.fullmatch(" fi le1_.py ")
    assert not r.fullmatch("file1py")

    r = f("*py")
    assert r.fullmatch("file1.py")
    assert r.fullmatch("fi le1 py")
    assert r.fullmatch(" fi le1_py")

    r = f("*py*")
    assert r.fullmatch("file1.py")
    assert r.fullmatch("fi le1 py ")
    assert r.fullmatch("python")
    assert not r.fullmatch("pyth/on")


@contextlib.contextmanager
def tmp_dirs(levels=1, files=1):
    """Returns tuple of directory name and list of all file names created in
    this directory, or even subdirectories"""
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
        [file_.close() for file_ in created_files]


def test_iterate_files():
    with tmp_dirs(levels=1) as (directory, files, dirs):
        files2 = [
            f for f in library.iterate_files(directory, include_dirs=False)
        ]
        assert (set(files)) == set(files2)
        files_and_dirs = [
            f for f in library.iterate_files(directory, include_dirs=True)
        ]
        assert set(files_and_dirs) == set(files) | set(dirs)
        assert list(library.iterate_files(
            tempfile.TemporaryDirectory().name)) == []
