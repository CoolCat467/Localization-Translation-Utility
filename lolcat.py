#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Lolcat Translator - Scrape lolcat translation website

"Lolcat Translator"

# Programmed by CoolCat467

__title__ = "Lolcat Scraper"
__author__ = "CoolCat467"
__version__ = "0.0.0"

from html.parser import HTMLParser
from typing import Any, Optional, Sequence

import mechanicalsoup
import trio

import extricate


async def gather(*tasks: Sequence) -> list:
    "Gather for trio."

    async def collect(index: int, task: list, results: dict[int, Any]) -> None:
        task_func, *task_args = task
        results[index] = await task_func(*task_args)

    results: dict[int, Any] = {}
    async with trio.open_nursery() as nursery:
        for index, task in enumerate(tasks):
            nursery.start_soon(collect, index, task, results)
    return [results[i] for i in range(len(tasks))]


class ResponseParser(HTMLParser):
    "Find tag with id and set self.value to data"

    def __init__(self, tag_type: str, search_id: str) -> None:
        super().__init__()

        self.search_tag_type = tag_type
        self.search_id = search_id
        self.found = False
        self.value: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        "Set found to True if tag type and id matches search"
        if tag == self.search_tag_type:
            creation = dict(attrs)
            if "id" not in creation:
                return
            if creation["id"] == self.search_id:
                self.found = True

    def handle_data(self, data: str) -> None:
        "Set value to value if currently handling target"
        if self.found:
            self.value = data

    def handle_endtag(self, tag: str) -> None:
        "Set found to false if end of search tag"
        if tag == self.search_tag_type and self.found:
            self.found = False


def translate_sentence(sentence: str) -> str:
    "Translate sentence"
    browser = mechanicalsoup.StatefulBrowser()
    browser.open("https://funtranslations.com/lolcat")
    browser.select_form("form#textform")
    browser["text"] = sentence
    response = browser.submit_selected()

    parser = ResponseParser("span", "lolcat")
    parser.feed(response.text)
    parser.close()

    value = parser.value
    if value is None:
        raise LookupError("Failed to find lolcat span in HTML response")
    if value.endswith(" ") and not sentence.endswith(" "):
        value = value[:-1]

    while " Srsly " in value:
        index = value.index(" Srsly ")
        if value[index - 1] == ",":
            value = value[: index - 1] + value[index:]
            index -= 1
        value = value[:index] + value[index + 7 :]

    if sentence[0].isupper():
        value = value[0].upper() + value[1:]

    return value.replace(".  ", ". ")


def translate_block(sentences: list[str], threshold: int = 2048) -> list[str]:
    "Translate sentences in bulk in batches if very big"
    sep = "^&^"
    result = []
    to_translate = list(reversed(sentences))
    while to_translate:
        block = ""
        while to_translate and len(block) < threshold:
            block += to_translate.pop() + sep
        if not block:
            break
        block = block[: -len(sep)]
        response = translate_sentence(block)
        result += response.split(sep)
    return result


def translate_file(english: dict, block_threshold: int = 2048) -> dict:
    "Translate an entire file."
    keys, sentences = extricate.dict_to_list(english)

    results = translate_block(sentences, block_threshold)

    for orig, new in zip(enumerate(sentences), results):
        idx, old = orig
        if new is None or not isinstance(old, str):
            results[idx] = old
            continue
        if old.endswith(" ") and not new.endswith(" "):
            results[idx] = new + " "
    return extricate.list_to_dict(keys, results)  # type: ignore


def run() -> None:
    "Run test of module"
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
