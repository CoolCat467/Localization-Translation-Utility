#!/usr/bin/env python3
# Tiny translator module using sneeky tricks from google's dictionary chrome extention
# -*- coding: utf-8 -*-

# Modified extensively by CoolCat467 from code in https://github.com/ssut/py-googletrans/issues/268

__title__ = 'Tiny tranlator module'
__author__ = 'CoolCat467'
__version__ = '0.0.2'
__ver_major__ = 0
__ver_minor__ = 0
__ver_patch__ = 2

import asyncio

import aiohttp
import async_timeout

import requests

from urllib.parse import urlencode

TIMEOUT = 30
MAGICHEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

class ResponseError(Exception):
    pass

def get_translation_url(sentance, tolanguage, fromlanguage='auto'):
    """Return the url you should visit to get sentance translated to language tolanguage."""
    query = {'client': 'dict-chrome-ex',
             'sl'    : fromlanguage,
             'tl'    : tolanguage,
             'q'     : sentance}
    url = 'https://clients5.google.com/translate_a/t?'+urlencode(query)
    return url

def translate(sentance, tolang, fromlang='auto'):
    """Use the power of sneeky tricks from chrome browser to do translation."""
    # Get url from function, which uses urllib to generate proper query
    url = get_translation_url(sentance, tolang, fromlang)
    try:
        # Make a get request to translate url with magic headers
        # that make it work right cause google is smart and looks at that.
        # Also, make request result be json so we can look at it easily
        request_result = requests.get(url, headers=MAGICHEADERS).json()
    except:
        # If it broke somehow, try again
        # NOTE: could cause indefinite recursion
        return translate(sentance, tolang, fromlang)
    # After we get the result, get the right field of the response and return that.
    # If result field not in request result
    if not 'alternative_translations' in request_result:
        # Raise an exception
        raise ResponseError('Invalid response, likely from an invalid language code')
    return request_result['alternative_translations'][0]['alternative'][0]['word_postproc']

async def get_translated_coroutine(loop, sentance, tolang, fromlang='auto'):
    """Return the sentance translated, asyncronously."""
    # Make a session with our event loop and the magic headers that make it work
    # right because google is smart and looks at that and expects us to be
    # the google translate dictionary extention running in google chrome.
    async with aiohttp.ClientSession(loop=loop, headers=MAGICHEADERS) as session:
        # Make sure we have a timeout, so that in the event of network failures
        # or something code doesn't get stuck
        async with async_timeout.timeout(TIMEOUT):
            # Get url from function, which uses urllib to generate proper query
            url = get_translation_url(sentance, tolang, fromlang)
            # Go to that url and get our translated response
            async with session.get(url) as response:
                # Wait for our response and make it json so we can look at
                # it like a dictionary
                request_result = await response.json()
                # Close response socket/file descriptor
                response.close()
        # Close session
        await session.close()
    # Get the result from the request result json
    # If result field not in request result
    if not 'alternative_translations' in request_result:
        # Raise an exception
        raise ResponseError('Invalid response, likely from an invalid language code')
    translated = request_result['alternative_translations'][0]['alternative'][0]['word_postproc']
    # Return that
    return translated

async def translate_async(loop, sentances, tolang, fromlang='auto'):
    """Translate multiple sentances asyncronously."""
    # Get a bunch of tasks running at once...
    coros = [get_translated_coroutine(loop, sentance, tolang, fromlang) for sentance in sentances]
    # then wait for all of them to finish. also asyncio.gather is awesome and
    # puts everything in order correctly somehow whew glad i don't have to do that
    return await asyncio.gather(*coros)

def translate_sentances(sentances, tolang, fromlang='auto'):
    """Translate many sentances at once using the power of asyncronous code."""
    # Get asyncronous event loop
    event_loop = asyncio.get_event_loop()
    # Run the main function until it's done and get our translated sentances
    data = event_loop.run_until_complete(
        translate_async(event_loop, sentances, tolang, fromlang)
    )
    # Return translated sentances
    return data

def run():
    """Demonstrate code usage and the power of asynchronous code."""
    print('\nHello. Welcome to our showing of how asynchronous code is faster than concurrent code.')
    
    # Quick make a nice little function stopwatch wrapper
    import time
    from functools import wraps
    def Timed(func):
        @wraps(func)
        def time_func(*args, **kwargs):
            start = time.perf_counter()
            result = func()
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
    srclang = 'en'
    dstlang = 'fr'
    
    print(f'... to the language corrosponding with language code "{dstlang}".')
    print('\nlettus begin.\n')
    
    # Define two functions, one that translates our sentances one at a time (normaly)
    @Timed
    def without_async():
        print('\n'.join(translate(sentance, dstlang, srclang) for sentance in sentances))
    # and another that does it all asyncronously, both timed.
    @Timed
    def with_async():
        print('\n'.join(translate_sentances(sentances, dstlang, srclang)))
    # Translate the sentances with both to prove asyncronous is better woo
    without_async()
    with_async()
    
    # Destroy the evidence! Mostly so nothing silly can happen when used as module.
    del with_async
    del without_async
    del Timed
    del wraps
    del time
    
    print('Now you know the way. dew it.')

if __name__ == '__main__':
    print('%s v%s\nProgrammed by %s.' % (__title__, __version__, __author__))
    run()
