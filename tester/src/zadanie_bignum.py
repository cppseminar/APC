"""Module for simplifying our unittests"""

import itertools
import os
import pathlib
import re
from typing import List, Iterable

DESCRIPTION = (
    f"Script which merges cpp file with all header files. "
    f"Point being, you have lots of headers and one cpp with main. "
)

HELP_FOLDER = (
    f"Folder with header files. "
)

HELP_MAIN = (
    f"Cpp file, containing main function. "
    f"Names of header files will be preprended to copies of this file. "
)

HELP_OUTPUT = (
    f"Output folder where cpp files will be placed. "
)

def build_file_regex(pattern: str):
    """We want to support only asterix as wildcard, so this function builds
    regex, from asterix only notation"""
    regex_parts: List[Iterable[str]] = [(re.escape(part), r'[\s\w]*')
                                        for part in pattern.split('*')]
    parts: List[str] = list(itertools.chain.from_iterable(regex_parts))
    parts.pop() # Last one is not asterix
    parts = ['^'] + parts + ['$']
    return re.compile(''.join(parts))

def iterate_folder(folder_path, wildcard='*.h'):
    """Return file names from FOLDER_PATH, matching WILDCARD. Paths are
    returned in format folder_path + file_name"""
    assert os.path.exists(folder_path), f"{folder_path}"
    with os.scandir(folder_path) as files:
        regex = build_file_regex(wildcard)
        for direntry in files:
            if not direntry.is_file() or not regex.fullmatch(direntry.name):
                continue
            yield direntry.path


def new_file_path(file_path, output_folder, suffix='cpp'):
    """Return new file path. Name of file is taken from FILE_PATH, folder
    path from OUTPUT_FOLDER and old suffixes are replaced with SUFFIX"""
    name = pathlib.Path(file_path).stem + "." + suffix
    out = pathlib.PurePath(os.path.realpath(output_folder))
    return out.joinpath(name)

def generate_include_line(header_file, cpp_file=None, relative=False):
    """Returns string in format #include "header_file". When RELATIVE is set,
    path is computed relative to cpp file. If not, it's just file name from
    HEADER_FILE"""
    if relative and not cpp_file:
        raise ValueError("When computing relative paths, cpp_file is required")
    if not cpp_file:
        cpp_file = pathlib.PurePosixPath("/") # Just random absolute path
    # Resolve paths if possible
    header_file = pathlib.PurePath(header_file)
    if os.path.exists(header_file):
        header_file = pathlib.PurePath(os.path.abspath(header_file))

    cpp_file = pathlib.PurePath(cpp_file)
    if os.path.exists(cpp_file):
        cpp_file = pathlib.PurePath(os.path.abspath(cpp_file))
    ############################

    # Paths must be absolute (when they don't exist)
    assert header_file.is_absolute() and cpp_file.is_absolute, 'Use absolute paths'

    if relative:
        line = os.path.relpath(header_file, cpp_file.parent)
    else:
        line = header_file.name
    line = '#include "' + str(line) + '"\n'
    return line


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('folder', metavar='Directory', type=str,
                        help=HELP_FOLDER)
    parser.add_argument('main', metavar='Cpp file', help=HELP_MAIN,
                        type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument('output', metavar='Output folder',
                        help=HELP_MAIN)
    args = parser.parse_args()

    main_content = ''

    # Read main
    with args.main:
        main_content = args.main.read()

    os.makedirs(os.path.abspath(args.output), exist_ok=True)

    for header in iterate_folder(args.folder):
        new_path = new_file_path(header, args.output, suffix='cpp')
        include_line = generate_include_line(header, new_path, relative=True)

        with open(new_path, "w") as f:
            f.writelines([include_line])
            f.write(main_content)
