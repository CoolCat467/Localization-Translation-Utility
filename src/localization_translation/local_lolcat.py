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


import re
from pathlib import Path
from typing import TypeVar

from localization_translation import extricate, lua_parser

# import lexer

T = TypeVar("T")

# LEXER: Final = lexer.Lexer()
# LEXER.add_token(lexer.Token("text", "[a-z|A-Z]+"))

### Tranzlashun.json from https://github.com/normansimonr/Dumb-Cogs/blob/master/lolz/data/tranzlashun.json
##with open("tranzlashun.json", encoding="utf-8") as trans_file:
##    TRANS_DICT: Final = json.load(trans_file)


PHRASES = [
    (re.compile(r" a ", re.I), " "),
    (re.compile(r"\bcan I have\b", re.I), "I can has"),
    (re.compile(r"\bcan I\b", re.I), "I can"),
    (re.compile(r"\bphoto", re.I), "foto"),
    (re.compile(r"\bit's", re.I), "it'z"),
    (re.compile(r"tion\b", re.I), "shun"),
    (re.compile(r"tions\b", re.I), "shuns"),
    (re.compile(r"sion\b", re.I), "shun"),
    (re.compile(r"ssion\b", re.I), "shun"),
    (re.compile(r"ssions\b", re.I), "shuns"),
    (re.compile(r"ion\b", re.I), "shun"),
    (re.compile(r"ions\b", re.I), "shuns"),
    (re.compile(r"ture\b", re.I), "chur"),
    (re.compile(r"ame\b", re.I), "aym"),
    (re.compile(r"ove\b", re.I), "oov"),
    (re.compile(r"per\b", re.I), "pah"),
    (re.compile(r"ary\b", re.I), "wee"),
    (re.compile(r"ery\b", re.I), "wee"),
    (re.compile(r"day\b", re.I), "dai"),
    (re.compile(r"ber\b", re.I), "bah"),
    (re.compile(r"er\b", re.I), "r"),
    (re.compile(r"ed\b", re.I), "d"),
    (re.compile(r"ad\b", re.I), "d"),
    (re.compile(r"\Bss\b", re.I), "s"),
    (re.compile(r"\Bs\b", re.I), "z"),
    (re.compile(r"\By\b", re.I), "i"),
    (re.compile(r"so\b", re.I), "os"),
    (re.compile(r"to\b", re.I), "ot"),
    (re.compile(r"ni\b", re.I), "in"),
    (re.compile(r"nu\b", re.I), "un"),
    # ending e swaps
    (re.compile(r"\Bae\b", re.I), "ea"),
    (re.compile(r"\Bbe\b", re.I), "eb"),
    (re.compile(r"\Bce\b", re.I), "ec"),
    (re.compile(r"\Bde\b", re.I), "ed"),
    (re.compile(r"\Bfe\b", re.I), "ef"),
    (re.compile(r"\Bge\b", re.I), "eg"),
    (re.compile(r"\Bhe\b", re.I), "eh"),
    (re.compile(r"\Bie\b", re.I), "ei"),
    (re.compile(r"\Bje\b", re.I), "ej"),
    (re.compile(r"\Bke\b", re.I), "ek"),
    (re.compile(r"\Ble\b", re.I), "el"),
    (re.compile(r"\Bme\b", re.I), "em"),
    (re.compile(r"\Bne\b", re.I), "en"),
    (re.compile(r"\Boe\b", re.I), "eo"),
    (re.compile(r"\Bpe\b", re.I), "ep"),
    (re.compile(r"\Bqe\b", re.I), "eq"),
    (re.compile(r"\Bre\b", re.I), "er"),
    (re.compile(r"\Bse\b", re.I), "z"),
    (re.compile(r"\Bte\b", re.I), "et"),
    (re.compile(r"\Bue\b", re.I), "eu"),
    (re.compile(r"\Bve\b", re.I), "ev"),
    (re.compile(r"\Bwe\b", re.I), "ew"),
    (re.compile(r"\Bxe\b", re.I), "ex"),
    (re.compile(r"\Bye\b", re.I), "ey"),
    (re.compile(r"\Bze\b", re.I), "ez"),
    #
    (re.compile(r"in\b", re.I), "en"),
    (re.compile(r"\Bing\b", re.I), "in"),
    (re.compile(r"\Bork\b", re.I), "erk"),
    (re.compile(r"ate\b", re.I), "ut"),
    (re.compile(r"ain", re.I), "ane"),
    (re.compile(r"with", re.I), "wif"),
    (re.compile(r"birth", re.I), "birf"),
]

WORDS = {
    "hi": "hai",
    "my": "mai",
    "the": "teh",
    "is": "iz",
    "please": "plz",
    "cheeseburger": "cheezburger",
    "are": "r",
    "have": "hav",
    "has": "haz",
    "ruler": "rulr",
    "of": "ov",
    "you": "u",
    "god": "Ceiling Cat",
    "cpu": "CUP",
    "gpu": "GUP",
    "mouse": "mices",
    "file": "fiel",
    "with": "wif",
    "new": "nu",
    "don't": "dun",
    "orange": "warmish",
    "dye": "powdr",
    "chest": "cat box",
    "to": "2",
    "from": "frum",
    "about": "bout",
    "one": "wan",
    "for": "4",
    "love": "luv",
    "your": "ur",
    "heart": "hart",
    "help": "halp",
    "be": "bees",
    "right": "riet",
    "and": "an",
    "world": "wurld",
    "light": "liet",
    "account": "akownt",
    "accounts": "akowntz",
    "who": "hoo",
    "what": "wut",
    "what's": "wut'z",
    "want": "wantz",
    "found": "findz",
    "word": "werd",
    "that": "dat",
    "until": "til",
    "try": "twie",
    "their": "der",
    "count": "cownt",
    "first": "furst",
    "person": "cat",
    "people": "catz",
    "quit": "kwyt",
    "recent": "resent",
    "height": "hiet",
    "exactly": "egsaktly",
    "background": "bakground",
    "hello": "y haol thar",
    "alpha": "alaf",
    "just": "jus",
    "say": "sai",
    "do": "doez",
    "get": "git",
    "should": "shud",
    "script": "skript",
    "between": "tween",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "github": "gifub",
    "many": "lotz",
    "them": "dem",
    "memory": "mems",
    "method": "mefod",
    "2fa": "2AF",
    "comma": "comam",
    "okay": "ok",
    "ok": "k",
    "oh": "o",
    "system": "sistem",
    "child": "kitteh",
    "children": "kittehz",
    "market": "markut",
    "friend": "frein",
    # fix
    "accountz": "akowntz",
    "what'z": "wut'z",
    "peopel": "catz",
    "em": "me",
    "thiz": "dis",
    "oen": "wan",
    "aer": "r",
    "eb": "bees",
    "thankz": "thx",
    "wallpaper": "wlpooper",
    "wallpaperz": "wlpooperz",
    "it'z": "iz",
    "haev": "haz",
    "somethin": "somefin",
    "soem": "sum",
    "theer": "thar",
    "befoer": "b4",
    "ot": "2",
    "phoen": "foen",
    "movei": "movai",
    "loov": "luv",
    "workz": "werkz",
    "mien": "miin",
    "aboov": "aboev",
    "oz": "OS",
    "os": "OS",
    "caz": "caez",
}
TRANS_DICT = WORDS


def replace_word(match: re.Match[str]) -> str:
    """Return the replacement word for the given match."""
    word = match.group(0)
    replacement = WORDS[word.lower()]
    if word.isupper():
        return replacement.upper()
    if word[:1].isupper():
        return replacement.capitalize()
    return replacement


WORD_PATTERN = re.compile(r"\b(" + "|".join(map(re.escape, WORDS)) + r")\b", re.I)


def lolcat(text: str) -> str:
    """Return lolcat translation of english sentance."""
    for pattern, replacement in PHRASES:
        text = pattern.sub(replacement, text)

    return WORD_PATTERN.sub(replace_word, text)


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


##def translate_sentence(sentence: str) -> str:
##    """Translate sentence. Not thread safe."""
##    LEXER.read_input(sentence)
##    new_sentence: list[str] = []
##    for token_type, text in LEXER.lex_input():
##        ##        print(f'{token_type}: {text}')
##        if token_type != "text":
##            if not new_sentence:
##                new_sentence.append("")
##            new_sentence[-1] += text
##            continue
##        lookup = text.casefold()
##        ##        print(lookup)
##        if lookup not in TRANS_DICT:
##            new_sentence.append(text)
##            UNCHANGED.add(lookup)
##        else:
##            new = TRANS_DICT[lookup]
##            new_sentence.append(match_case(text, new))
##    return " ".join(new_sentence)

translate_sentence = lolcat


IGNORE_CHANGE: set[str] = set()


##def add_unchanged() -> None:
##    """Update translation dictionary from lolcat scraper."""
##    global IGNORE_CHANGE
##    import lolcatscraper
##
##    values = list(UNCHANGED.difference(IGNORE_CHANGE))
##    results = lolcatscraper.translate_block(values)
##    ##    sep = '^&^'
##    ##    sentence = sep.join(values)
##    ##    results = lolcatscraper.translate_sentence(sentence)
##    ##    results = [x.strip() for x in result.split(sep)]
##    results = [x.strip() for x in results]
##    rewrite = False
##    for orig, new in zip(values, results, strict=True):
##        if orig != new:
##            print(f'"{orig}" -> "{new}"')
##            TRANS_DICT[orig.lower()] = new
##            UNCHANGED.remove(orig)
##            rewrite = True
##    print(f"Still unchanged: {UNCHANGED}")
##    IGNORE_CHANGE |= UNCHANGED
##    UNCHANGED.clear()
##    if rewrite:
##        with open("tranzlashun.json", "w", encoding="utf-8") as trans_file:
##            json.dump(TRANS_DICT, trans_file)
##    del lolcatscraper


def translate_block(sentences: list[str]) -> list[str]:
    """Translate sentences in bulk in batches if very big."""
    return [translate_sentence(sentence) for sentence in sentences]


def translate_file(english: dict[str, T]) -> dict[str, T]:
    """Translate an entire file."""
    keys, sentences = extricate.dict_to_list(english)

    results = translate_block(sentences)

    for orig, new in zip(enumerate(sentences), results, strict=True):
        idx, old = orig
        ##        if new is None or not isinstance(old, str):
        ##            results[idx] = old
        ##            continue
        if old.endswith(" ") and not new.endswith(" "):
            results[idx] = new + " "
    ##    add_unchanged()
    return extricate.list_to_dict(keys, results)  # type: ignore


def read_lua(path: Path) -> dict[str, str]:
    """Return localization dictonary from reading specified lua file."""
    with path.open(encoding="utf-8") as fp:
        tokens = lua_parser.tokenize(fp.read())
    parser = lua_parser.Parser(list(tokens))
    value = parser.parse_value()
    result, _tokens = lua_parser.parse_lua_table(value)
    assert isinstance(result, dict)
    return result


def run() -> None:
    """Run test of module."""
    text = [
        "This is hearsay!",
        "This is a test.",
        "I am the way, the truth, and the life. No one comes to God except through me.",
        "You understand, mechanical hands are the ruler of everything",
        "Do you swear to say the complete truth, the whole truth, and nothing but the truth?",
        "Lime green terricotta",
        "Orange dye",
        "Chest",
    ]

    ##    print(text)
    ##    print(translate_block(text))
    for line in text:
        print(line)
        # print(translate_sentence(line))
        print(lolcat(line))
        print()

    here = Path(__file__).absolute()
    localizations = here.parent / "mineos_cache" / "Localizations"
    english_data = read_lua(localizations / "English.lang")
    lolcat_data = read_lua(localizations / "Lolcat.lang")

    for key, value in english_data.items():
        lolcat_value = lolcat_data[key]
        current_result = lolcat(value)
        if lolcat_value == value:
            if current_result == value:
                continue
            ##            print(key)
            print(value)
            print(current_result)
            print()
        elif current_result != lolcat_value:
            print(key)
            print(f"[en]  {value}")
            print(f"[new] {current_result}")
            print(f"[cur] {lolcat_value}")
            print()


##        else:
##            print(f"{key} match")


if __name__ == "__main__":
    print(f"{__title__}\nProgrammed by {__author__}.\n")
    run()
