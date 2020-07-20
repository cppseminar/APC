"""Module containing useful functions used across testscripts."""
import collections
import contextlib
import itertools
import pathlib
import re
import tempfile
import weakref
from typing import List, Iterable, Optional, Tuple

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


# pylint: disable=unused-argument
def noop(*args, **kwargs):
    """Do NOTHING."""
    return None
# pylint: enable=unused-argument


class GlobalTmpFolder:
    """Class resembling TemporaryDirectory, but always returns same directory.

    Class has same methods and attributes as TemporaryDirectory.  BUT, only
    cleans directory, if it is empty.
    """

    _NAME: Optional[pathlib.Path] = None
    _FIRST_ARGS: Optional[Tuple[str, str, str]] = None
    _DELETER = None

    class ScopeGuard:
        """When instance of this class is deleted, function is called."""

        def __init__(self, func):
            """Call func on self destruction."""
            weakref.finalize(self, func)

    def __init__(self, *, prefix=None, suffix=None, directory=None):
        """Initialize internal variables.

        Check whether GlobalTmpFolder was in this program run created with same
        parameters.  If not throw ValueError.
        """
        args = (suffix, prefix, directory)
        if GlobalTmpFolder._FIRST_ARGS is None:  # This is first invocation
            GlobalTmpFolder._FIRST_ARGS = args
            GlobalTmpFolder._NAME = pathlib.Path(tempfile.mkdtemp(*args))
            GlobalTmpFolder._DELETER = GlobalTmpFolder.ScopeGuard(
                lambda: self.cleanup(self._NAME))

        self.name = str(self._NAME)

        if GlobalTmpFolder._FIRST_ARGS != args:
            raise ValueError(f"Currently you must call {self.__class__} "
                             f"always with same arguments")

    @staticmethod
    def cleanup(directory_name: pathlib.Path):
        """Delete directory if it is empty, swallows os exception."""
        with contextlib.suppress(OSError):
            directory_name.rmdir()
            GlobalTmpFolder._FIRST_ARGS = None
            GlobalTmpFolder._NAME = None

    def __str__(self):
        """Behave as mkdtemp result, ie. return file path."""
        return self.name
