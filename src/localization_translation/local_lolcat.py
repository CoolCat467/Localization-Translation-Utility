"""Lolcat Translator - Scrape lolcat translation website."""

# Programmed by CoolCat467

from __future__ import annotations

# Lolcat Translator - Scrape lolcat translation website
# Copyright (C) 2023-2024  CoolCat467
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

__title__ = "Lolcat Scraper"
__author__ = "CoolCat467"
__version__ = "0.0.0"
__license__ = "GNU General Public License Version 3"


import json
from typing import Final, TypeVar

import extricate
import lexer

T = TypeVar("T")

LEXER: Final = lexer.Lexer()
LEXER.add_token(lexer.Token("text", "[a-z|A-Z]+"))

# Tranzlashun.json from https://github.com/normansimonr/Dumb-Cogs/blob/master/lolz/data/tranzlashun.json
with open("tranzlashun.json", encoding="utf-8") as trans_file:
    TRANS_DICT: Final = json.load(trans_file)


def match_case(orig: str, new: str) -> str:
    """Mace new first char match case of orig first char."""
    if not new or not orig:
        return new
    if orig.endswith(" ") and not new.endswith(" "):
        new += " "
    if all(x.isupper() for x in orig):
        return new.upper()
    up = orig[0].isupper()
    if up and not new[0].isupper():
        return new.capitalize()
    if not up and new[0].isupper():
        return new.lower()
    return new


UNCHANGED: set[str] = set()


def translate_sentence(sentence: str) -> str:
    """Translate sentence. Not thread safe."""
    LEXER.read_input(sentence)
    new_sentence: list[str] = []
    for token_type, text in LEXER.lex_input():
        ##        print(f'{token_type}: {text}')
        if token_type != "text":  # noqa: S105
            if not new_sentence:
                new_sentence.append("")
            new_sentence[-1] += text
            continue
        lookup = text.casefold()
        ##        print(lookup)
        if lookup not in TRANS_DICT:
            new_sentence.append(text)
            UNCHANGED.add(lookup)
        else:
            new = TRANS_DICT[lookup]
            new_sentence.append(match_case(text, new))
    return " ".join(new_sentence)


IGNORE_CHANGE: set[str] = set()


def add_unchanged() -> None:
    """Update translation dictionary from lolcat scraper."""
    global IGNORE_CHANGE
    import lolcatscraper

    values = list(UNCHANGED.difference(IGNORE_CHANGE))
    results = lolcatscraper.translate_block(values)
    ##    sep = '^&^'
    ##    sentence = sep.join(values)
    ##    results = lolcatscraper.translate_sentence(sentence)
    ##    results = [x.strip() for x in result.split(sep)]
    results = [x.strip() for x in results]
    rewrite = False
    for orig, new in zip(values, results, strict=True):
        if orig != new:
            print(f'"{orig}" -> "{new}"')
            TRANS_DICT[orig.lower()] = new
            UNCHANGED.remove(orig)
            rewrite = True
    print(f"Still unchanged: {UNCHANGED}")
    IGNORE_CHANGE |= UNCHANGED
    UNCHANGED.clear()
    if rewrite:
        with open("tranzlashun.json", "w", encoding="utf-8") as trans_file:
            json.dump(TRANS_DICT, trans_file)
    del lolcatscraper


def translate_block(sentences: list[str]) -> list[str]:
    """Translate sentences in bulk in batches if very big."""
    return [translate_sentence(sentence) for sentence in sentences]


def translate_file(english: dict[str, T]) -> dict[str, T]:
    """Translate an entire file."""
    keys, sentences = extricate.dict_to_list(english)

    results = translate_block(sentences)

    for orig, new in zip(enumerate(sentences), results, strict=True):
        idx, old = orig
        if new is None or not isinstance(old, str):
            results[idx] = old
            continue
        if old.endswith(" ") and not new.endswith(" "):
            results[idx] = new + " "
    ##    add_unchanged()
    return extricate.list_to_dict(keys, results)  # type: ignore


def run() -> None:
    """Run test of module."""
    text = [
        "This is hearsay!",
        "I am the way, the truth, and the life. No one comes to God except through me.",
        "You understand, mechanical hands are the ruler of everything",
        "Do you swear to say the complete truth, the whole truth, and nothing but the truth?",
    ]
    print(text)
    print(translate_block(text))


if __name__ == "__main__":
    print(f"{__title__}\nProgrammed by {__author__}.\n")
    run()
