"""Module containing useful functions used across testscripts."""
import re
import itertools
import pathlib
import collections
from typing import List, Iterable


def build_file_regex(pattern: str):
    """We want to support only asterix as wildcard, so this function builds
    regex, from asterix only notation.  Will match only file names (no / in
    names...)"""
    regex_parts: List[Iterable[str]] = [(re.escape(part), r'[^<>:"/\\|?*]*')
                                        for part in pattern.split('*')]
    parts: List[str] = list(itertools.chain.from_iterable(regex_parts))
    parts.pop()  # Last one is not asterix
    parts = ['^'] + parts + ['$']
    return re.compile(''.join(parts))


def iterate_files(directory, depth=0, include_dirs=True):
    """Iterator returning all files in directory as pathlib.Path. Traverses
    also subdirectories up to depth=DEPTH.

    If DEPTH is 0, then goes as far as possible.

    INCLUDE DIRS specifies if directories should also be returned.  Even if
    INCLUDE_DIRS is false, directories and their files are iterated - but
    directory names are not returned (yielded)
    """
    depth = int(depth)
    directory = pathlib.Path(directory)
    assert depth >= 0
    assert directory.exists() and directory.is_dir()

    directories = collections.deque()
    directories.append(directory)
    seen_directories = collections.deque()  # Next level of directories
    current_level = 0

    while depth == 0 or current_level < depth:
        current_level += 1
        directories.extend(seen_directories)  # Current level of dirs
        seen_directories = collections.deque()  # Next level of directories

        while directories:
            directory = directories.popleft()
            for path in directory.iterdir():
                if path.is_dir():
                    seen_directories.append(path)
                    if not include_dirs:
                        continue
                yield path

        # If there are no more directories
        if not seen_directories:
            return


def filter_files(iterable: Iterable, wildcard: str = "*"):
    """Given ITERABLE with file names, filter those that do not match
    wildcard.

    Wildcard is approximately something like unix shell expansion - asterix
    means anything, rest are normal chars """
    regex = build_file_regex(wildcard)

    def _filter(filename):
        name = pathlib.PurePath(filename).name
        return bool(regex.fullmatch(name))

    return filter(_filter, iterable)
