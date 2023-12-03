# Convert all text files in folder to LF line ending
import sys
import argparse
import pathlib
import fnmatch
import io
from typing import List, Any, Iterable, Tuple

# Source of this ascii map is open source file utility.
#
# https://github.com/file/file/blob/master/src/encoding.c
# https://www.darwinsys.com/file/
#
# Original map distinguishes ASCII, ISO-8859 and non-ISO extended ASCII.  These
# symbols are here all marked as 1

_ASCII_MAP = [
    #                   BEL BS HT LF VT FF CR
    0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0,  # 0x01
    #                               ESC
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,  # 0x11
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x21
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x31
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x41
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x51
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x61
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,  # 0x71
    #             NEL
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x81
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x91
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0xa1
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0xb1
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0xc1
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0xd1
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0xe1
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1  # 0xf1
];

if len(_ASCII_MAP) != 256:
    print("Error bad ascii map size")
    exit(1)

DESCRIPTION = """fold2lf - convert text files in folder to linux line endings"""
_VERBOSE = 0  # Dynamic variable, changed during argument parsing
_BLACK_BLOBS = []


def print_verbose(log: str) -> None:
    if _VERBOSE > 2:
        print(log)


def _folder_exists(path: str) -> pathlib.Path:
    """Plugs to argparser. Converts path to pathlib.Path if exists and is
    directory. Throws otherwise"""
    folder_path = pathlib.Path(path)
    if folder_path.exists() and folder_path.is_dir():
        return folder_path.absolute()
    raise ValueError(f"folder name error ('{folder_path}')")


def build_arguments():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--folder",
        action="store",
        required=True,
        type=_folder_exists,
        help="Folder containing text files",
    )
    parser.add_argument(
        '-v',
        action='append_const',
        const=1,
        help="Verbose level 0 - quiet, 1 - stats, 2 - verbose, 3 - debug",
        default=list())
    parser.add_argument(
        "--ignore-pattern",
        action="append",
        required=False,
        dest="patterns",
        default=list(),
        help="Specify (unix like - glob) pattern, e.g. *.py, to ignore files")
    return parser


def get_files(path: pathlib.Path) -> List[pathlib.Path]:
    """Recursively retrieves all files from directory and subdirectory. Returns
    only files (no folders, pipes etc.)"""
    print_verbose(f"Listing folder {path}")
    all_entries = path.glob("**/*")
    return list(filter(lambda x: x.is_file(), sorted(all_entries)))


def glob_list(pattern_list: List[str], iterable: Iterable[str]) -> List[bool]:
    """Check if any pattern in pattern list matches iterable. Returns bool list
    of ITERABLE size. List contains True for matched values, False
    otherwise."""
    result = list()
    for path in iterable:
        matched = False
        for pattern in pattern_list:
            print_verbose(f"{path} matching pattern '{pattern}'?")
            if fnmatch.fnmatch(path, pattern):
                matched = True
                print_verbose(f"YES")
                break
        result.append(matched)
    return result


def to_relative(basepath: pathlib.Path, relpath: pathlib.Path) -> str:
    """Return relative path from base to relpath."""
    pure = pathlib.PurePath(relpath)
    return str(pure.relative_to(basepath))


def _check_hit(data: bytes, map: List[bool]) -> bool:
    """Returns True if data hits zero."""
    for byte in data:
        if map[byte] == 0:
            return True
    return False


def is_text(path: pathlib.Path) -> bool:
    """Check whether file content looks to be text only."""
    with open(path, "rb") as f:
        reader = io.BufferedReader(f)
        while data := reader.read(1024):
            if _check_hit(data, _ASCII_MAP):
                return False
    return True


def delete_cr(path: pathlib.Path):
    """Deletes carriage returns (\r) from text file."""
    tmp_path = pathlib.Path(f"{path}.tmp")
    with open(path, "rb") as inputf:
        with open(tmp_path, "wb") as outputf:
            while data := inputf.read(1024):
                data = data.replace(b'\r', b'')
                outputf.write(data)
    tmp_path.rename(path)


def _detect_binary(names: List[pathlib.Path], dont_check: List[bool]) -> List[bool]:
    """"""
    results: List[bool] = list()
    for path, dontc in zip(names, dont_check):
        if dontc:
            results.append(False)
            continue
        results.append(not is_text(path))
    return results

def print_files(detections: List[Tuple[pathlib.Path, bool, bool]]):
    """Print list of files, of verbose setting is on."""
    def print_them(f):
        for path, is_ignored, is_binary in detections:
            if f(is_ignored, is_binary):
                print(path)
    if _VERBOSE < 2:
        return
    print("Ignored files")
    print_them(lambda ignored, binary: ignored)
    print("--------------")
    print("Binary files")
    print_them(lambda ignored, binary: not ignored and binary)
    print("--------------")
    print("Text files")
    print_them(lambda ignored, binary: not ignored and not binary)
    print("--------------")

if __name__ == "__main__":
    arg_parser = build_arguments()
    parsed_args = arg_parser.parse_args()
    _VERBOSE = len(parsed_args.v)
    _BLACK_BLOBS += parsed_args.patterns
    print_verbose(f"Ignore files patterns: {_BLACK_BLOBS}")
    #####
    base_path: pathlib.Path = parsed_args.folder
    all_files: List[pathlib.Path] = get_files(base_path)
    matched: List[bool] = glob_list(
        _BLACK_BLOBS, map(lambda x: to_relative(base_path, x), all_files))
    ####
    are_text: List[bool] = _detect_binary(all_files, matched)
    # Detections contains tuple of (path, is_ignored, is_binary)
    detections: List[Tuple[pathlib.Path, bool, bool]] = list(zip(all_files, matched, are_text))
    print_files(detections)
    # Write
    for path, is_ignored, is_binary in detections:
        if not is_ignored and not is_binary:
            delete_cr(path)
