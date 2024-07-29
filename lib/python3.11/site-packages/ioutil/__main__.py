from __future__ import annotations

import os
import ast
import sys
import argparse
from srutil import util
from typing import Any

from . import File, __version__, __package__


def _epilog() -> str:
    return """-w/--write function may return error as it expects data in specific datatype. 
           Writing files using commandline isn't recommended."""


def get_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=__package__, usage=util.stringbuilder(__package__, " [options]"),
                                     epilog=_epilog())
    parser.add_argument('-v', '--version', action='version', help='show version number and exit.', version=__version__)
    group = parser.add_argument_group("to read/write files")
    group.add_argument("path", type=str, help="path to read/write")
    group.add_argument("-r", "--read", dest="read", default=False, action="store_true", help="to read file")
    group.add_argument("-w", "--write", dest="write", default=False, action="store_true", help="to write file")
    group.add_argument("-d", "--data", metavar='', help="data to write")
    group.add_argument("-f", "--format", dest='format', metavar='', choices=['csv', 'json', 'parquet', 'text', 'toml'],
                       type=str, required=False, help="file format to use")
    group.add_argument("-m", "--mode", dest="mode", metavar='', default=None, help="mode to open file")
    group.add_argument("--rfv", dest="rfv", default=False, action="store_true",
                       help="will return formatted string (CSV only)")
    parser.add_argument_group(group)
    options = parser.parse_args()
    if not options.format:
        _ext = list(os.path.splitext(options.path)).pop()
        _format = {".csv": "csv", ".json": "json", ".parquet": ".parquet", ".toml": "toml", ".txt": "text"}
        if _ext not in _format:
            parser.error("the following arguments are required: -f/--format")
        else:
            options.format = _format.get(_ext)
    if not options.read and not options.write:
        parser.error("one of the following arguments are required: -r/--read or -w/--write")
    if options.read and options.write:
        parser.error("any one of the following arguments should be given: -r/--read or -w/--write")
    if options.write and not options.data:
        parser.error("the following arguments are required: -d/--data")
    return options


def _get_data(_data: str, _format: str) -> Any:
    return _data if _format == 'text' else ast.literal_eval(_data)


def main():
    options = get_argument()
    mode = options.mode if options.mode else None
    if options.read:
        print(File.read(options.path, _format=options.format, mode=mode, _rfv=options.rfv))
    elif options.write:
        data = _get_data(options.data, options.format)
        print(File.write(data, options.path, _format=options.format, mode=mode))


if __name__ == "__main__":
    sys.exit(main())
