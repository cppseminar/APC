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
def tmp_dirs(levels=1, files=5):
    """Returns tuple of directory name and list of all file names created in
    this directory, or even subdirectories"""
    directories = []
    created_files = []
    file_names = []
    main_dir = tempfile.TemporaryDirectory()
    directory = main_dir.name
    for _ in range(levels):
        directories.append(tempfile.TemporaryDirectory(prefix='dir', dir=directory))
        directories.append(tempfile.TemporaryDirectory(prefix='dir', dir=directory))
        for _ in range(files):
            file_1 = tempfile.NamedTemporaryFile(dir=directories[-1].name, delete=False)
            file_2 = tempfile.NamedTemporaryFile(dir=directories[-2].name, delete=False)
            created_files.append(file_1)
            created_files.append(file_2)
            file_names.append(pathlib.Path(file_1.name))
            file_names.append(pathlib.Path(file_2.name))

        # Make also second level
        directory = directories[-1].name

    yield main_dir.name, file_names
    for file_ in created_files:
        file_.close()
    for directory in reversed(directories):
        directory.cleanup()


def test_iterate_files():
    with tmp_dirs(levels=1) as (directory, files):
        from pprint import pprint
        files2 = [f for f in library.iterate_files(directory, include_dirs=False)]
        assert (sorted(files)) == sorted(files2)
