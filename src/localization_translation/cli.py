"""CLI - Command Line Interface."""

# Programmed by CoolCat467

from __future__ import annotations

# CLI - Command Line Interface
# Copyright (C) 2024  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__title__ = "CLI - Command Line Interface"
__author__ = "CoolCat467"
__license__ = "GNU General Public License Version 3"


import argparse
import logging
from typing import TYPE_CHECKING

import httpx
import trio

from localization_translation.mineos_auto_trans import (
    __version__,
    translate_broken_values,
    translate_lolcat,
    translate_main,
    translate_new_value,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class ListAction(argparse.Action):
    """List supported badges action."""

    __slots__ = ()

    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str = argparse.SUPPRESS,
        default: str = argparse.SUPPRESS,
        help: str = "list supported badges and exit",  # noqa: A002  # `help` is shadowing a Python builtin
    ) -> None:
        """Initialize this action."""
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        _namespace: argparse.Namespace,
        _values: str | Sequence[object] | None,
        _option_string: str | None = None,
    ) -> None:
        """Print badges and exit."""
        parser.exit()


class DumpAction(argparse.Action):
    """Dump badge data action."""

    __slots__ = ()

    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str = argparse.SUPPRESS,
        default: str = argparse.SUPPRESS,
        help: str = "dump badge data",  # noqa: A002  # `help` is shadowing a Python builtin
    ) -> None:
        """Initialize this action."""
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        _namespace: argparse.Namespace,
        _values: str | Sequence[object] | None,
        _option_string: str | None = None,
    ) -> None:
        """Print json dump of badges and exit."""
        parser.exit()


async def async_run(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
) -> None:
    """Async entry point."""
    async with httpx.AsyncClient(http2=True) as client:
        if args.unhandled:
            print("Translating Unhandled Values...")
            await translate_main(client)
        elif args.broken:
            print("Translating Broken Values...")
            await translate_broken_values(client)
        elif args.lolcat:
            print("Translating Lolcat...")
            await translate_lolcat(client)
        elif args.filename and args.key:
            print(f"Translating new key {args.key!r} in file {args.filename!r}...")
            await translate_new_value(client, args.key, args.filename)
    parser.exit(0)


def main() -> None:
    """Handle command line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-u",
        "--unhandled",
        action="store_true",
        help="Translate unhandled languages",
    )
    group.add_argument(
        "-b",
        "--broken",
        action="store_true",
        help="Translate broken values",
    )
    group.add_argument(
        "-l",
        "--lolcat",
        action="store_true",
        help="Translate to lolcat",
    )
    new_key_group = parser.add_argument_group()
    new_key_group.add_argument(
        "-f",
        "--filename",
        dest="filename",
    )
    new_key_group.add_argument(
        "-k",
        "--key",
        dest="key",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)

    is_new_key = args.filename and args.key
    if not (args.unhandled or args.broken or args.lolcat or is_new_key):
        parser.print_help()
        parser.exit(1)
    if is_new_key and (args.unhandled or args.broken or args.lolcat):
        parser.print_help()
        parser.exit(1, "Translate new key and other translate type is mutually exclusive.")
    trio.run(async_run, parser, args, strict_exception_groups=True)


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
    main()
