#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"Tiny translator module"

__title__ = 'Tiny tranlator module'
__author__ = 'CoolCat467'

import json
import random
import asyncio
from urllib.parse import urlencode
import urllib.request
from typing import Final, Any, Callable, Optional

import aiohttp

import agents

TIMEOUT: Final[int] = 4
AGENT = random.randint(0, 100000)

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
    # Get url from function, which uses urllib to generate proper query
    url = get_translation_url(sentance, to_lang, source_lang)
    f = urllib.request.urlopen(url, timeout=0.5)
    request_result = json.loads(f.read())
    f.close()
    return process_response(request_result)

async def get_translated_coroutine(session, sentance: str, to_lang: str,
                                   source_lang='auto') -> str:
    "Return the sentance translated, asyncronously."
    global AGENT
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
            async with session.request('GET', url, ssl=False, headers=headers) as response:
                # Wait for our response and make it json so we can look at
                # it like a dictionary
                return process_response(await response.json())
        except asyncio.exceptions.TimeoutError:
            pass

async def translate_async(loop, sentances: list, to_lang: str,
                          source_lang: str='auto', timeout: int=TIMEOUT) -> list:
    "Translate multiple sentances asyncronously."
    # Get a bunch of tasks running at once...
    timeout_obj = aiohttp.ClientTimeout(timeout)
    
##    # Debug trace config
##    trace_config = aiohttp.TraceConfig()
##
##    for name in [n for n in dir(trace_config) if n.startswith('on_') and not 'dns' in n]:
##        def make_me_log(name):
##            log_name = ' '.join(map(lambda x: x.title(), name.split('_')[1:]))
##            async def log_thing(session, trace_config_ctx, params):
##                print('#'*32)
##                print(log_name)
##                print(f'\n{session = }\n')
##                print(f'{trace_config_ctx = }\n')
##                print(f'{params = }')
##                print('#'*32+'\n')
##            return log_thing
##        getattr(trace_config, name).append(make_me_log(name))
    
    async with aiohttp.ClientSession(loop=loop, timeout=timeout_obj
##                                     trace_configs=[trace_config]
                                     ) as session:
        coros = [get_translated_coroutine(session, q, to_lang, source_lang) for q in sentances]
        # then wait for all of them to finish. also asyncio.gather is awesome and
        # puts everything in order correctly somehow whew glad i don't have to do that
        return await asyncio.gather(*coros)

def translate_sentances(sentances: list, to_lang: str,
                        source_lang: str='auto', timeout: int=TIMEOUT) -> list:
    "Translate many sentances at once using the power of asyncronous code."
    # Get asyncronous event loop
    event_loop = asyncio.new_event_loop()
    # Run the main function until it's done and get our translated sentances
    data = event_loop.run_until_complete(
        translate_async(event_loop, sentances, to_lang, source_lang, timeout)
    )
    # Close event loop
    event_loop.close()
    # Return translated sentances
    return data

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
    @timed
    def with_async() -> None:
        timeout = 1.5
        print('\n'.join(translate_sentances(sentances, dst_lang, src_lang, timeout)))
    
    without_async()
    with_async()

if __name__ == '__main__':
    print(f'{__title__} \nProgrammed by {__author__}.')
    run()
