#!/usr/bin/env python3
# Tiny translator module using sneeky tricks from google's dictionary chrome extention
# -*- coding: utf-8 -*-

"Translate: Tiny translator module"

# Modified extensively by CoolCat467 from code in https://github.com/ssut/py-googletrans/issues/268

__title__ = 'Tiny tranlator module'
__author__ = 'CoolCat467'
__version__ = '0.1.0'
__ver_major__ = 0
__ver_minor__ = 1
__ver_patch__ = 0

import asyncio
from urllib.parse import urlencode
from typing import Final, Any, Callable, Optional

# typecheck: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
import requests
import aiohttp
import async_timeout


TIMEOUT: Final[int] = 30
MAGIC_HEADER: Final[dict] = {
    # pylint: disable=line-too-long
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

def get_translation_url(sentance: str, to_language: str, source_language: str='auto') -> str:
    "Return the url you should visit to get query translated to language to_language."
    query = {'client': 'dict-chrome-ex',
             'sl'    : source_language,
             'tl'    : to_language,
             'q'     : sentance}
    return 'https://clients5.google.com/translate_a/t?'+urlencode(query)

def process_response(result: list) -> str:
    "Return string after processing response."
##    return request_result['alternative_translations'][0]['alternative'][0]['word_postproc']
    return result[0]

def translate_sync(sentance: str, to_lang: str, source_lang: str='auto') -> str:
    "Use the power of sneeky tricks from chrome browser to do translation."
    # Get url from function, which uses urllib to generate proper query
    url = get_translation_url(sentance, to_lang, source_lang)
    # Make a get request to translate url with magic headers
    # that make it work right because google is smart and looks at that.
    # Also, make request result be json so we can look at it easily
    request_result = requests.get(url, headers=MAGIC_HEADER).json()
    return process_response(request_result)

async def get_translated_coroutine(loop, sentance: str, to_lang: str, source_lang='auto') -> str:
    "Return the sentance translated, asyncronously."
    # Make a session with our event loop and the magic headers that make it work
    # right because google is smart and looks at that and expects us to be
    # the google translate dictionary extention running in google chrome.
    async with aiohttp.ClientSession(loop=loop, headers=MAGIC_HEADER) as session:
        # Make sure we have a timeout, so that in the event of network failures
        # or something code doesn't get stuck
        async with async_timeout.timeout(TIMEOUT):
            # Get url from function, which uses urllib to generate proper query
            url = get_translation_url(sentance, to_lang, source_lang)
            # Go to that url and get our translated response
            async with session.get(url) as response:
                # Wait for our response and make it json so we can look at
                # it like a dictionary
                request_result = await response.json()
                # Close response socket/file descriptor
                response.close()
        # Close session
        await session.close()
    return process_response(request_result)

async def translate_async(loop, sentances: list, to_lang: str, source_lang: str='auto') -> list:
    "Translate multiple sentances asyncronously."
    # Get a bunch of tasks running at once...
    coros = [get_translated_coroutine(loop, q, to_lang, source_lang) for q in sentances]
    # then wait for all of them to finish. also asyncio.gather is awesome and
    # puts everything in order correctly somehow whew glad i don't have to do that
    return await asyncio.gather(*coros)

def translate_sentances(sentances: list, to_lang: str, source_lang: str='auto') -> list:
    "Translate many sentances at once using the power of asyncronous code."
    # Get asyncronous event loop
    event_loop = asyncio.new_event_loop()
    # Run the main function until it's done and get our translated sentances
    data = event_loop.run_until_complete(
        translate_async(event_loop, sentances, to_lang, source_lang)
    )
    # Close event loop
    event_loop.close()
    # Return translated sentances
    return data

def run() -> None:
    "Demonstrate code usage and the power of asynchronous code."
    print('\nHello. Welcome to the translation demo.')
    
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
    sentances = ['Hello', 'Goodbye', 'Cat',
                 'You understand, mechanical hands are the ruler of everything',
                 'Hello World!', 'Eggs', 'Spam', 'I can has cheeseburgers please',
                 'Over the rainbow', 'Muffin time', 'Lolcat is too a language!',
                 'This is a test', 'Asynchronous code is faster hazah']
    # Tell the person watching us what they are
    print('We will be translating the following sentances...\n')
    print('\n'.join(sentances)+'\n')
    # We will be translating from english to french
    src_lang = 'en'
    dst_lang = 'fr'
    
    print(f'... to the language corrosponding with language code "{dst_lang}".')
    print('\nlettus begin.\n')
    
    # Define two functions, one that translates our sentances one at a time (normaly)
    @timed
    def without_async() -> None:
        print('\n'.join(translate_sync(sentance, dst_lang, src_lang) for sentance in sentances))
    # and another that does it all asyncronously, both timed.
    @timed
    def with_async() -> None:
        print('\n'.join(translate_sentances(sentances, dst_lang, src_lang)))
    # Translate the sentances with both to prove asyncronous is better woo
    
    if input('\nWould you like a demonstration of the translate module? (y/N) : ').lower() != 'y':
        return
    
    without_async()
    with_async()

if __name__ == '__main__':
    print(f'{__title__} v{__version__}\nProgrammed by {__author__}.')
    run()
