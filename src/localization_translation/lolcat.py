"""Lolcat Translator - Scrape lolcat translation website."""

# Programmed by CoolCat467

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

from __future__ import annotations

__title__ = "Lolcat Scraper"
__author__ = "CoolCat467"
__version__ = "0.0.0"
__license__ = "GNU General Public License Version 3"


from html.parser import HTMLParser
from typing import TYPE_CHECKING, Any, TypeVar

import mechanicalsoup
import trio

from localization_translation import extricate

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")


async def gather(*tasks: Sequence) -> list:
    """Gather for trio."""

    async def collect(index: int, task: list, results: dict[int, Any]) -> None:
        task_func, *task_args = task
        results[index] = await task_func(*task_args)

    results: dict[int, Any] = {}
    async with trio.open_nursery() as nursery:
        for index, task in enumerate(tasks):
            nursery.start_soon(collect, index, task, results)
    return [results[i] for i in range(len(tasks))]


class ResponseParser(HTMLParser):
    """Find tag with id and set self.value to data."""

    def __init__(self, tag_type: str, search_id: str) -> None:
        """Initialize Response Parser."""
        super().__init__()

        self.search_tag_type = tag_type
        self.search_id = search_id
        self.found = False
        self.value: str | None = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        """Set found to True if tag type and id matches search."""
        if tag == self.search_tag_type:
            creation = dict(attrs)
            if "id" not in creation:
                return
            if creation["id"] == self.search_id:
                self.found = True

    def handle_data(self, data: str) -> None:
        """Set value to value if currently handling target."""
        if self.found:
            self.value = data

    def handle_endtag(self, tag: str) -> None:
        """Set found to false if end of search tag."""
        if tag == self.search_tag_type and self.found:
            self.found = False


def translate_sentence(sentence: str) -> str:
    """Translate sentence."""
    if not sentence.strip():
        return sentence

    browser = mechanicalsoup.StatefulBrowser(soup_config={"features": "html.parser"})
    browser.open("https://funtranslations.com/lolcat")
    browser.select_form("form#textform")
    browser["text"] = sentence
    response = browser.submit_selected()

    parser = ResponseParser("span", "lolcat")
    parser.feed(response.text)
    parser.close()

    value = parser.value
    if value is None:
        exc = LookupError("Failed to find lolcat span in HTML response")
        exc.add_note(f"{sentence = }")
        exc.add_note(response.text)
        raise exc
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
    """Translate sentences in bulk in batches if very big."""
    sep = "^&^"
    result = []
    to_translate = tuple(sentences)
    while to_translate:
        block = ""
        block_count = 0
        while block_count < len(to_translate) and len(block) < threshold:
            block += to_translate[block_count] + sep
            block_count += 1
        if not block:
            break
        block = block.removesuffix(sep)
        response = translate_sentence(block)
        block_result = response.split(sep)
        ##        assert len(block_result) == block_count, f"{len(block_result)} != {block_count}"
        if len(block_result) != block_count:
            print("Something broke, manually going through one by one")
            for sentence in to_translate[:block_count]:
                translated = translate_sentence(sentence)
                print(f"{sentence!r} -> {translated!r}")
                result.append(translated)
        else:
            result.extend(block_result)
        ##        print(f'{len(to_translate) - block_count = }')
        to_translate = to_translate[block_count:]
    ##        print(f'{len(to_translate) = }')
    ##        result.append(translate_sentence(to_translate.pop()))
    if len(result) != len(sentences):
        for idx in range(max(len(result), len(sentences))):
            if idx < len(sentences):
                print(repr(sentences[idx]), end="")
            print(" --> ", end="")
            if idx < len(result):
                print(repr(result[idx]), end="")
            print()
    assert len(result) == len(sentences), f"{len(result)} != {len(sentences)}"
    return result


def translate_file(english: dict[str, T], block_threshold: int = 2048) -> dict[str, T]:
    """Translate an entire file."""
    keys, sentences = extricate.dict_to_list(english)

    # There apparently exist some bad values somewhere, strip those out
    bad_values = set()
    good_values = []
    for idx, sentence in enumerate(sentences):
        if isinstance(sentence, str) and sentence.strip():
            good_values.append(idx)
        else:
            bad_values.add(idx)

    # Only translate non-blanks
    translate_sentences = [sentences[idx] for idx in good_values]

    ##    # Handle duplicate values
    ##    duplicate_values = {}
    ##    translate_sentences = []
    ##    for idx in good_values:
    ##        sentence = sentences[idx]
    ##        if sentence in translate_sentences:
    ##            duplicate_values[idx] = translate_sentences.index(sentence)
    ##        else:
    ##            translate_sentences.append(sentence)

    translate_results = translate_block(translate_sentences, block_threshold)

    ##    # Rebuild with duplicate values
    ##    translate_results = []
    ##    for deduped_index, idx in enumerate(good_values):
    ##        duplicate_entry = duplicate_values.get(idx)
    ##        if duplicate_entry is not None:
    ##            translate_results.append(translate_results[duplicate_entry])
    ##        else:
    ##            translate_results.append(translate_deduplicated_results[deduped_index])

    # Rebuild full results with blanks
    results = []
    index = 0
    for idx, original in enumerate(sentences):
        if idx in bad_values:
            results.append(original)
        else:
            results.append(translate_results[index])
            index += 1

    for (idx, old), new in zip(enumerate(sentences), results, strict=True):
        if new is None or not isinstance(old, str):
            results[idx] = old
            continue
        if old.endswith(" ") and not new.endswith(" "):
            results[idx] = new + " "
    assert len(results) == len(sentences)
    ##    print("\n".join(" --> ".join(x) for x in zip(sentences, results)))
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
