"""Module containing useful functions used across testscripts."""
import collections
import itertools
import pathlib
import re
import tempfile
from typing import Any, Dict, List, Iterable, Optional

# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods

def build_file_regex(pattern: str):
    """Create regex from unix like pattern.

    We want to support only asterix as wildcard, so this function builds
    regex, from asterix only notation.  Will match only file names (no / in
    names...)
    """
    regex_parts: List[Iterable[str]] = [(re.escape(part), r'[^<>:"/\\|?*]*')
                                        for part in pattern.split('*')]
    parts: List[str] = list(itertools.chain.from_iterable(regex_parts))
    parts.pop()  # Last one is not asterix
    parts = ['^'] + parts + ['$']
    return re.compile(''.join(parts))


def iterate_files(directory, depth=0, include_dirs=True):
    """Iterate files in DIRECTORY and return as pathlib.Path.

    Traverses also subdirectories up to depth=DEPTH.

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
    """Filter ITERABLE with file names, return those matching wildcard.

    Wildcard is approximately something like unix shell expansion - asterix
    means anything, rest are normal chars. For more info check function
    build_file_regex.
    """
    regex = build_file_regex(wildcard)

    def _filter(filename):
        name = pathlib.PurePath(filename).name
        return bool(regex.fullmatch(name))

    return filter(_filter, iterable)


def str_to_valid_file_name(supposed_name: str) -> str:
    """Cut from SUPPOSED_NAME all invalid characters.

    Characters invalid for for windows. (Pretty much superset of everythin
    else).  Unfortunately we are not checking here everything, and invalid
    names still can happen on occasion. :(
    """
    mapping = {
        ord('<'): '',
        ord('>'): '',
        ord(':'): '',
        ord('"'): '',
        ord('/'): '',
        ord('\\'): '',
        ord('|'): '',
        ord('?'): '',
        ord('*'): ''
    }
    return str(supposed_name).translate(mapping).strip()


class GlobalTmpFolder:
    """Wrapper around TemporaryDirectory, always returns same directory.

    Class has same methods and attributes as TemporaryDirectory.

    This is also sooo bad for mutlithreading, but who cares ;)
    """

    _NAMED_FOLDERS: Optional[tempfile.TemporaryDirectory] = None
    _FIRST_DICT: Optional[Dict[str, Any]] = None

    def __init__(self, **kwargs):
        """Initilize internal TemporaryDirectory.

        Check whether GlobalTmpFolder was in this program run created with same
        parameters.  If not throw ValueError.
        """
        if GlobalTmpFolder._FIRST_DICT is None:  # This is first invocation
            GlobalTmpFolder._FIRST_DICT = kwargs
            GlobalTmpFolder._NAMED_FOLDERS = tempfile.TemporaryDirectory(
                **kwargs)

        if GlobalTmpFolder._FIRST_DICT != kwargs:
            raise ValueError(f"Currently you must call {self.__class__} "
                             f"always with same arguments")

    def __getattribute__(self, name):
        """Forward all calls to internal TemporaryDirectory."""
        return GlobalTmpFolder._NAMED_FOLDERS.__getattribute__(name)


if __name__ == '__main__':
    GlobalTmpFolder()
