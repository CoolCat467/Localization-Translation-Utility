#!/usr/bin/env python3

"""Tiny translator module"""

__title__ = "Tiny translator module"
__author__ = "CoolCat467"


import json
import random
import urllib.request
from collections.abc import Coroutine, Sequence
from functools import partial
from typing import Any, Final
from urllib.parse import urlencode

import agents
import httpx
import trio

TIMEOUT: Final[int] = 4
AGENT = random.randint(0, 100000)  # noqa: S311


async def gather(*tasks: partial[Coroutine[Any, Any, Any]]) -> list[Any]:
    """Gather for trio."""

    async def collect(
        index: int,
        task: partial[Coroutine[Any, Any, Any]],
        results: dict[int, Any],
    ) -> None:
        results[index] = await task()

    results: dict[int, Any] = {}
    async with trio.open_nursery() as nursery:
        for index, task in enumerate(tasks):
            nursery.start_soon(collect, index, task, results)
    return [results[i] for i in range(len(tasks))]


##def get_translation_url(sentence: str, to_language: str, source_language: str='auto') -> str:
##    "Return the url you should visit to get query translated to language to_language."
##    query = {'client': 'dict-chrome-ex',
##             'sl'    : source_language,
##             'tl'    : to_language,
##             'q'     : sentence}
##    return 'http://clients5.google.com/translate_a/t?'+urlencode(query)


def get_translation_url(sentence: str, to_language: str, source_language: str = "auto") -> str:
    """Return the URL you should visit to get query translated to language to_language."""
    query = {
        "client": "gtx",
        "dt": "t",
        "sl": source_language,
        "tl": to_language,
        "q": sentence,
    }
    return "https://translate.googleapis.com/translate_a/single?" + urlencode(query)


def process_response(result: list[str] | list[list[Any]]) -> str:
    """Return string after processing response."""
    part = result
    while isinstance(part, list):
        next_ = part[0]
        if isinstance(next_, str):
            return next_
        if isinstance(next_, list):
            part = next_
        else:
            raise ValueError(f"Unexpected type {type(part)!r}, expected list or str")


def is_url(text: str) -> bool:
    """Return True if text is probably a URL."""
    return text.startswith("http") and "://" in text and "." in text and " " not in text


def translate_sync(sentence: str | int, to_lang: str, source_lang: str = "auto") -> str | int:
    """Synchronously perform translation of sentence from source_lang to to_lang"""
    if isinstance(sentence, int) or is_url(sentence):
        # skip numbers and URLs
        return sentence

    # Get URL from function, which uses urllib to generate proper query
    url = get_translation_url(sentence, to_lang, source_lang)
    if not url.startswith("http"):
        raise ValueError("URL not http(s), is this intended?")
    with urllib.request.urlopen(url, timeout=0.5) as file:  # noqa: S310
        request_result = json.loads(file.read())
    return process_response(request_result)


async def get_translated_coroutine(
    client: httpx.AsyncClient,
    sentence: str | int,
    to_lang: str,
    source_lang: str = "auto",
) -> str | int:
    """Return the sentence translated, asynchronously."""
    global AGENT  # pylint: disable=global-statement

    if isinstance(sentence, int) or is_url(sentence):
        # skip numbers and URLs
        return sentence
    # Make sure we have a timeout, so that in the event of network failures
    # or something code doesn't get stuck
    # Get URL from function, which uses urllib to generate proper query
    url = get_translation_url(sentence, to_lang, source_lang)

    headers = {
        "User-Agent": "",
        "Accept": "*/*",
        "Accept-Language": "en-US,en-GB; q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    while True:
        AGENT = (AGENT + 1) % len(agents.USER_AGENTS)
        headers["User-Agent"] = agents.USER_AGENTS[AGENT]

        try:
            # Go to that URL and get our translated response
            response = await client.get(url, headers=headers)
            # Wait for our response and make it json so we can look at
            # it like a dictionary
            return process_response(response.json())
        except httpx.ConnectTimeout:
            pass
        except json.decoder.JSONDecodeError:
            print(f"{type(response) = }\n{response = }")
            raise


async def translate_async(
    client: httpx.AsyncClient,
    sentences: Sequence[str | int],
    to_lang: str,
    source_lang: str,
) -> list[str | int]:
    """Translate multiple sentences asynchronously."""
    coros = [partial(get_translated_coroutine, client, q, to_lang, source_lang) for q in sentences]
    return await gather(*coros)


async def async_run() -> None:
    """Async entry point"""
    async with httpx.AsyncClient(http2=True) as client:
        input_ = ["cat is bob", "bob is a potato"]
        print(f"{input_ = }")
        result = await translate_async(client, input_, "fr", "en")
        print(f"{result = }")


def run() -> None:
    """Main entry point"""
    # import trio.testing
    trio.run(async_run)  # , clock=trio.testing.MockClock(autojump_threshold=0))


if __name__ == "__main__":
    print(f"{__title__} \nProgrammed by {__author__}.")
    run()
