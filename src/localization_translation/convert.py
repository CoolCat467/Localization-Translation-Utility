"""Convert - Lua Table Conversion to and from Python Dictionaries."""

# Programmed by CoolCat467

from __future__ import annotations

# Convert - Lua Table Conversion to and from Python Dictionaries
# Copyright (C) 2022-2024  CoolCat467
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

__title__ = "Convert"
__author__ = "CoolCat467"
__version__ = "1.4.2"
__license__ = "GNU General Public License Version 3"


import json
from typing import Any


def squish(text: str) -> str:
    """Remove all newlines and tabs from text."""
    return text.translate({10: "", 9: ""})


def split_squished(squished_text: str) -> str:
    """Split text with {} and , with no indent or newlines into separate lines."""
    lines = []
    indent = 0
    cline = ""

    def cartrage_return() -> None:
        """Add current line with indent."""
        nonlocal cline
        lines.append("\t" * indent + f"{cline}\n")
        cline = ""

    for char in squished_text:
        match char:
            case "{":
                cline += char
                cartrage_return()
                indent += 1
            case "}":
                cartrage_return()
                cline += char
                indent -= 1
            case ",":
                cline += char
                cartrage_return()
            case _:
                cline += char
    cartrage_return()
    return "".join(lines)[:-1]


def lang_to_json(
    lang_data: str,
) -> tuple[dict[str, Any], dict[str, dict[int, str]]]:
    """Fix language data to be readable by json parser. Return data and comments."""
    if not lang_data[-1]:
        lang_data = lang_data[:-1]
    lines = lang_data.splitlines()

    new_lines = []
    comments: dict[str, dict[int, str]] = {}
    for line in lines:
        if "{" in line and "}" in line:
            n_indent = line.count("\t") * "\t"
            nline = line.replace("{", f"{{\n{n_indent}")
            nline = nline.replace("}", f"\n{n_indent}}}")
            data = nline.splitlines()
            ndata = []
            square = True
            for dline in data[1:-1]:
                dline = dline.strip()
                if "=" in dline:
                    square = False
                for value in dline.split(","):
                    value = value.strip()
                    if not square:
                        key, value = value.split("=")
                        key = key.strip()
                        value = value.strip()
                        value = f"{key} = {value}"
                    ndata.append(f"{n_indent}\t{value}")
            nline = "\n".join((data[0], ",\n".join(ndata), data[-1]))
            new_lines += nline.splitlines()
            continue
        new_lines.append(line)
    lines, new_lines = new_lines, []

    section = [("null", 0)]
    close_stack: list[bool] = []

    for lidx, line in enumerate(lines):
        idx = len(new_lines)

        if section:
            offset = lidx - section[-1][1]
            path = "/".join(s[0] for s in section)

            # Remember comments by section block and offset from start
            if "--" in line:
                comment = line.split("--")[1].strip()

                if path not in comments:
                    comments[path] = {}

                comments[path][offset] = comment
                continue
            # Remember empty lines as empty comment
            if line.strip() == "":
                if path not in comments:
                    comments[path] = {}

                comments[path][offset] = ""
                continue
            # In both cases do not continue parsing line
        if "=" in line:  # Setting new item
            key, value = line.split("=", 1)

            indent = key.count("\t")
            n_indent = "\t" * indent

            key = key.strip()
            value = value.strip()

            if key.startswith("[") and key.endswith("]"):
                key = key[1:-1]

                # VK app has strange thing,
                # [0] index defined in what is read as list
                # because Lua tables are incredibly powerful
                # but a mess to deal with in Python.

                # This basically is hack to add four $ to end
                # of value that undo process will find
                # and fix for us

                # TODO: Properly handle mixed table. Not sure how
                # to store as python object though.
                if close_stack[-1] and key == "0":  # If supposed to be list
                    com = False
                    string = False
                    if value.endswith(","):
                        value = value[:-1]
                        com = True
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                        string = True
                    value += "$$$$"
                    if string:
                        value = f'"{value}"'
                    if com:
                        value += ","

                    new_lines.append(f"{n_indent}{value}")
                    continue
            if value.startswith("{"):  # If starting new table
                # Remember section
                section.append((key, lidx))
                # Find next line defining data
                nidx = lidx + 1
                while nidx < len(lines):
                    nline = lines[nidx].strip()
                    if not nline.startswith("--"):
                        break
                    nidx += 1
                # See if list or dictionary (has '=')
                square = "=" not in nline
                close_stack.append(square)
                # change accordingly
                if square:
                    value = value.replace("{", "[")
            line = f'{n_indent}"{key}": {value}'
        elif "}" in line:  # End of section
            prev = new_lines[idx - 1]
            if prev.endswith(","):  # Remove unneeded trailing comma
                new_lines[idx - 1] = prev[:-1]
            if close_stack.pop():  # Close section type properly
                line = line.replace("}", "]", 1)
            section.pop()
        elif "{" in line:  # Start of new section but no index set
            section.append(("dict", lidx))
            # Find next line defining data
            nidx = lidx + 1
            while nidx < len(lines):
                nline = lines[nidx].strip()
                if not nline.startswith("--"):
                    break
                nidx += 1
            # See if list or dictionary (has '=')
            square = "=" not in nline
            close_stack.append(square)
            # change accordingly
            if square:
                line = line.replace("{", "[", 1)
        new_lines.append(line)
    json_text = "\n".join(new_lines)
    # print(json_text)
    try:
        return json.loads(json_text), comments
    except json.JSONDecodeError:
        print(json_text)
        raise


def dict_to_lang(
    data: dict[str, Any],
    comments: dict[str, dict[int, str]],
) -> str:
    """Convert data and comments to MineOS file data."""
    json_data = json.dumps(
        data,
        ensure_ascii=False,
        indent="\t",
        separators=(",", " = "),
    )
    new_lines: list[str] = []
    section: list[tuple[str, int]] = [("null", 0)]
    for line in json_data.splitlines():
        idx = len(new_lines)

        indent = line.count("\t") * "\t"

        if " = " in line and line.split(" = ")[1].strip() == "[" or line.strip() == "[":
            line = line.replace("[", "{", 1)
        if line.strip() in {"],", "]"}:
            line = line.replace("]", "}", 1)

        if "{" in line:
            key = "dict"
            if " = " in line:
                key = line.split(" = ", 1)[0].strip()
                if key.startswith('"') and key.endswith('"'):
                    key = key[1:-1]
            section.append((key, idx))

        if "}" in line:
            path = "/".join(s[0] for s in section)
            sec_start = section.pop()[1]
            if path in comments:
                for offset, comment in comments[path].items():
                    pos = sec_start + offset
                    indent = "" if pos >= len(new_lines) else new_lines[pos].count("\t") * "\t"
                    comment = f"{indent}-- {comment}" if comment else indent
                    new_lines.insert(pos, comment)

        if " = " in line:
            key, value = line.split(" = ", 1)
            key = key.strip()

            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
            if key.isdigit():
                key = f"[{key}]"

            line = f"{indent}{key} = {value}"

        # VK app has strange thing
        if "$$$$" in line:
            value = line.strip().replace("$$$$", "", 1)
            line = f"{indent}[0] = {value}"
        new_lines.append(line)

    for _ in range(len(section)):
        path = "/".join(s[0] for s in section)
        sec_start = section.pop()[1]
        if path in comments:
            for offset, comment in comments[path].items():
                pos = sec_start + offset
                indent = "" if pos >= len(new_lines) else new_lines[pos].count("\t") * "\t"

                comment = f"{indent}-- {comment}" if comment else indent
                new_lines.insert(pos, comment)

    return "\n".join(new_lines)


def update_comment_positions(
    original_pos: dict[str, dict[int, str]],
    new_data: dict[str, Any],
    old_data: dict[str, Any],
) -> dict[str, dict[int, str]]:
    """Update comment positions."""
    # Get json text of files
    old_json = json.dumps(old_data, indent="\t").splitlines()
    new_json = json.dumps(new_data, indent="\t").splitlines()

    new_comments: dict[str, dict[int, str]] = {}

    # For each name
    for name in old_data:
        # Reads include comments, so have to keep track of comments read.
        read_offset = 0

        # Make predictions of guess where it is in new version more accurate
        sec_add = 0

        # Find section
        section = "null/"
        for item in original_pos:
            if name in item:
                section = item

        # If sections of data are not the same
        if new_data[name] != old_data[name]:
            # Find start of bock section in new and old json
            section_start = f'\t"{name}": ['
            obs = old_json.index(section_start) - 1
            nbs = new_json.index(section_start) - 1
            n_end = new_json.index("\t]") + 1
            # Initialize section
            new_comments[section] = {}
            # For each offset in the comments
            for offset in sorted(original_pos[section]):
                # Find line comment lives on
                old_comment = old_json[obs + offset - read_offset]

                # Find start to look for same line in new
                start = nbs + offset - read_offset + sec_add
                start = max(nbs, start)

                # Find old comment position in new json
                new_pos = new_json.index(old_comment, start, n_end)

                # Cumulative additions
                sec_add = max(sec_add, new_pos - start)

                # New position needs to be offset as well
                new_pos += read_offset

                # Update offset
                read_offset += 1

                # Record new comment
                new_comments[section][new_pos - nbs] = original_pos[section][offset]
    return new_comments


def read_lang_file(
    filepath: str,
) -> tuple[dict[str, Any], dict[str, dict[int, str]]]:
    """Read MineOS data file."""
    with open(filepath, encoding="utf-8") as file_point:
        fdata = file_point.read()
    return lang_to_json(fdata)


def write_lang_file(
    filepath: str,
    data: dict[str, Any],
    comments: dict[str, dict[int, str]],
) -> None:
    """Write MineOS data file."""
    with open(filepath, "w", encoding="utf-8") as file_point:
        file_point.write(dict_to_lang(data, comments))


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
