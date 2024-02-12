#!/usr/bin/env python3
# Lolcat Translator - Scrape lolcat translation website

"""Lolcat Translator"""

# Programmed by CoolCat467

__title__ = "Lolcat Scraper"
__author__ = "CoolCat467"
__version__ = "0.0.0"

import json
from typing import Final

import extricate
import lexer

LEXER: Final = lexer.Lexer()
LEXER.add_token(lexer.Token("text", "[a-z|A-Z]+"))

# Tranzlashun.json from https://github.com/normansimonr/Dumb-Cogs/blob/master/lolz/data/tranzlashun.json
with open("tranzlashun.json", encoding="utf-8") as trans_file:
    TRANS_DICT: Final = json.load(trans_file)


def match_case(orig: str, new: str) -> str:
    """Mace new first char match case of orig first char"""
    if not new or not orig:
        return new
    if orig.endswith(" ") and not new.endswith(" "):
        new += " "
    if all([x.isupper() for x in orig]):
        return new.upper()
    up = orig[0].isupper()
    if up and not new[0].isupper():
        return new.capitalize()
    if not up and new[0].isupper():
        return new.lower()
    return new


UNCHANGED = set()


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


IGNORE_CHANGE = set()


def add_unchanged() -> None:
    """Update translation dictionary from lolcat scraper"""
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
    """Translate sentences in bulk in batches if very big"""
    return [translate_sentence(sentence) for sentence in sentences]


def translate_file(english: dict) -> dict:
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
    """Run test of module"""
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
