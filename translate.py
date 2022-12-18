#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"Tiny translator module"

__title__ = 'Tiny tranlator module'
__author__ = 'CoolCat467'


from typing import Final, Any, Sequence

import json
import random
from urllib.parse import urlencode
import urllib.request

import trio
import httpx

import agents


TIMEOUT: Final[int] = 4
AGENT = random.randint(0, 100000)


async def gather(*tasks: Sequence[Any]) -> list[Any]:
    "Gather for trio."
    async def collect(index: int, task: list[Any], results: dict[int, Any]) -> None:
        task_func, *task_args = task
        results[index] = await task_func(*task_args)
    
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


def get_translation_url(sentence: str,
                        to_language: str,
                        source_language: str = 'auto') -> str:
    "Return the URL you should visit to get query translated to language to_language."
    query = {'client': 'gtx',
             'dt'    : 't',
             'sl'    : source_language,
             'tl'    : to_language,
             'q'     : sentence}
    return 'https://translate.googleapis.com/translate_a/single?'+urlencode(query)


def process_response(result: list[str] | list[list[Any]]) -> str:
    "Return string after processing response."
    part = result
    while isinstance(part, list):
        next_ = part[0]
        if isinstance(next_, list):
            part = next_
        elif isinstance(next_, str):
            return next_
    return part  # type: ignore[unreachable]


def is_url(text: str) -> bool:
    "Return True if text is probably a URL."
    return text.startswith('http') and '://' in text and '.' in text and not ' ' in text


def translate_sync(sentence: str | int, to_lang: str, source_lang: str='auto') -> str | int:
    "Synchronously preform translation of sentence from source_lang to to_lang"
    if isinstance(sentence, int) or is_url(sentence):
        # skip numbers and URLs
        return sentence
    
    # Get URL from function, which uses urllib to generate proper query
    url = get_translation_url(sentence, to_lang, source_lang)
    with urllib.request.urlopen(url, timeout=0.5) as file:
        request_result = json.loads(file.read())
    return process_response(request_result)


async def get_translated_coroutine(client: httpx.AsyncClient,
                                   sentence: str | int, to_lang: str,
                                   source_lang: str='auto') -> str | int:
    "Return the sentence translated, asynchronously."
    global AGENT# pylint: disable=global-statement
    
    if isinstance(sentence, int) or is_url(sentence):
        # skip numbers and URLs
        return sentence
    # Make sure we have a timeout, so that in the event of network failures
    # or something code doesn't get stuck
    # Get URL from function, which uses urllib to generate proper query
    url = get_translation_url(sentence, to_lang, source_lang)
    
    headers = {
        'User-Agent': '',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en-GB; q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    while True:
        AGENT = (AGENT + 1) % len(agents.USER_AGENTS)
        headers['User-Agent'] = agents.USER_AGENTS[AGENT]
        
        try:
            # Go to that URL and get our translated response
            response = await client.get(url, headers=headers)
            # Wait for our response and make it json so we can look at
            # it like a dictionary
            return process_response(response.json())
        except httpx.ConnectTimeout:
            pass
        except json.decoder.JSONDecodeError:
            print(f'{type(response) = }')
            print(f'{response = }')
            raise


async def translate_async(client: httpx.AsyncClient,
                          sentences: list[str | int], to_lang: str,
                          source_lang: str) -> list[str | int]:
    "Translate multiple sentences asynchronously."
    coros = [(get_translated_coroutine, client, q, to_lang, source_lang)
             for q in sentences]
    return await gather(*coros)


if __name__ == '__main__':
    print(f'{__title__} \nProgrammed by {__author__}.')
