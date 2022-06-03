#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"Tiny translator module"

__title__ = 'Tiny tranlator module'
__author__ = 'CoolCat467'

import json
import random
from urllib.parse import urlencode
import urllib.request
from typing import Final, Any, Callable

import trio
import httpx

import agents

TIMEOUT: Final[int] = 4
AGENT = random.randint(0, 100000)

async def gather(*tasks):
    "Gather for trio."
    async def collect(index, task, results):
        task_func, *task_args = task
        results[index] = await task_func(*task_args)
    
    results = {}
    async with trio.open_nursery() as nursery:
        for index, task in enumerate(tasks):
            nursery.start_soon(collect, index, task, results)
    return [results[i] for i in range(len(tasks))]

##def get_translation_url(sentance: str, to_language: str, source_language: str='auto') -> str:
##    "Return the url you should visit to get query translated to language to_language."
##    query = {'client': 'dict-chrome-ex',
##             'sl'    : source_language,
##             'tl'    : to_language,
##             'q'     : sentance}
##    return 'http://clients5.google.com/translate_a/t?'+urlencode(query)

def get_translation_url(sentance: str, to_language: str, source_language: str='auto') -> str:
    "Return the url you should visit to get query translated to language to_language."
    query = {'client': 'gtx',
             'dt'    : 't',
             'sl'    : source_language,
             'tl'    : to_language,
             'q'     : sentance}
    return 'https://translate.googleapis.com/translate_a/single?'+urlencode(query)

def process_response(result: list) -> str:
    "Return string after processing response."
##    return result[0]
    part = result
    while isinstance(part, list):
        part = part[0]
    return part

def translate_sync(sentance: str, to_lang: str, source_lang: str='auto') -> str:
    "Syncronously preform translation of sentance from source_lang to to_lang"
    if isinstance(sentance, int):
        # skip numbers
        return sentance
    
    # Get url from function, which uses urllib to generate proper query
    url = get_translation_url(sentance, to_lang, source_lang)
    with urllib.request.urlopen(url, timeout=0.5) as file:
        request_result = json.loads(file.read())
    return process_response(request_result)

async def get_translated_coroutine(client, sentance: str, to_lang: str,
                                   source_lang='auto') -> str:
    "Return the sentance translated, asyncronously."
    global AGENT# pylint: disable=global-statement
    
    if isinstance(sentance, int):
        # skip numbers
        return sentance
    # Make sure we have a timeout, so that in the event of network failures
    # or something code doesn't get stuck
    # Get url from function, which uses urllib to generate proper query
    url = get_translation_url(sentance, to_lang, source_lang)
    
    headers = {
        'User-Agent': None,
        'Accept': '*/*',
        'Accept-Language': 'en-US,en-GB; q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    while True:
        AGENT = (AGENT + 1) % len(agents.USER_AGENTS)
        headers['User-Agent'] = agents.USER_AGENTS[AGENT]
        
        try:
            # Go to that url and get our translated response
            response = await client.get(url, headers=headers)
            # Wait for our response and make it json so we can look at
            # it like a dictionary
            return process_response(response.json())
        except httpx.ConnectTimeout:
            pass

async def translate_async(client, sentances: list, to_lang: str, source_lang: str) -> list:
    "Translate multiple sentances asyncronously."
    coros = [(get_translated_coroutine, client, q, to_lang, source_lang) for q in sentances]
    return await gather(*coros)

def run() -> None:
    "Demonstrate code usage and the power of asynchronous code."    
    # Quick make a nice little function stopwatch wrapper
    # pylint: disable=import-outside-toplevel
    import time
    from functools import wraps
    
    def timed(func) -> Callable[..., Any]:
        @wraps(func)
        def time_func(*args, **kwargs) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            stop = time.perf_counter()
            print(f'\n{func.__name__} took {stop-start:.4f} secconds.\n')
            return result
        return time_func
    
    # Get a bunch of sentances to translate
    sentances = ['Good morning', 'I would like to buy a muffin', 'bye']
    # Tell the person watching us what they are
    print('\nWe will be translating the following sentances...\n')
    print('\n'.join(sentances)+'\n')
    # We will be translating from english to french
    src_lang = 'en'
    dst_lang = 'fr'
    
    print(f'... to the language corrosponding with language code "{dst_lang}".\n')
    
    # Define two functions, one that translates our sentances one at a time (normaly)
    @timed
    def without_async() -> None:
        print('\n'.join(translate_sync(sentance, dst_lang, src_lang) for sentance in sentances))
    # and another that does it all asyncronously, both timed.
##    @timed
##    def with_async() -> None:
##        timeout = 1.5
##        print('\n'.join(translate_sentances(sentances, dst_lang, src_lang, timeout)))
    
    without_async()
##    with_async()

if __name__ == '__main__':
    print(f'{__title__} \nProgrammed by {__author__}.')
    run()
