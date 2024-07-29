from __future__ import annotations

import os
import sys
import argparse
from srutil import util

from . import Local, __version__, __package__


def get_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=__package__, usage=util.stringbuilder(__package__, " [options]"), )
    parser.add_argument('-v', '--version', action='version', help='show version number and exit.', version=__version__)
    group = parser.add_argument_group("to browse local files")
    group.add_argument("keys", nargs='+', help="keyword to search")
    group.add_argument("-p", "--path", metavar='', dest="path", default=os.getcwd(), required=True, help="root path")
    group.add_argument("-n", "--no-prompt", dest="noprompt", default=True, action="store_false",
                       help="do not interactively prompt for choice")
    parser.add_argument_group(group)
    options = parser.parse_args()
    return options


def main():
    options = get_argument()
    local = Local(options.path)
    local.search(*options.keys, display=True, prompt=options.noprompt)


if __name__ == "__main__":
    sys.exit(main())
