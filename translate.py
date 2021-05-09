#!/usr/bin/env python3
# Tiny translator module using sneeky tricks from google's dictionary chrome extention
# -*- coding: utf-8 -*-

# Modified extensively by CoolCat467 from code in https://github.com/ssut/py-googletrans/issues/268

__title__ = 'Tiny tranlator module'
__author__ = 'CoolCat467'
__version__ = '0.0.0'
__ver_major__ = 0
__ver_minor__ = 0
__ver_patch__ = 0

import asyncio

import aiohttp
import async_timeout

import requests

from urllib.parse import urlencode

TIMEOUT = 60
MAGICHEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

def get_translation_url(sentance, tolanguage, fromlanguage='auto'):
    """Return the url you should visit to get sentance translated to language tolanguage."""
    query = {'client': 'dict-chrome-ex',
             'sl'    : fromlanguage,
             'tl'    : tolanguage,
             'q'     : sentance}
    url = 'https://clients5.google.com/translate_a/t?'+urlencode(query)
    
##    sentance = '%20'.join(sentance.split(' '))
##    url = "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl="+fromlanguage+"&tl="+tolanguage+"&q=" + sentance
    return url

def translate(sentance, tolang, fromlang='auto'):
    """Use the power of sneeky tricks from chrome browser to do translation."""
    # Get url from function, which uses urllib to generate proper query
    url = get_translation_url(sentance, tolang, fromlang)
    try:
        # Make a get request to translate url with magic headers that make it work right cause it's smart and looks at that
        # also, make request result be json so we can look at it easily
        request_result = requests.get(url, headers=MAGICHEADERS).json()
    except:
        # If it broke somehow, try again - NOTE: could cause indefinite recursion
        return translate(sentance, tolang, fromlang)
    # After we get the result, get the right field of the response and return that.
    return request_result['alternative_translations'][0]['alternative'][0]['word_postproc']

async def get_translated_coroutine(loop, sentance, tolang, fromlang='auto'):
    """Return the sentance translated, asyncronously."""
    # Make a session with our event loop and the magic headers that make it work right cause it's smart
    async with aiohttp.ClientSession(loop=loop, headers=MAGICHEADERS) as session:
        # Make sure we have a timeout, so that in the event of network failures or something code doesn't get stuck
        async with async_timeout.timeout(TIMEOUT):
            # Get url from function, which uses urllib to generate proper query
            url = get_translation_url(sentance, tolang, fromlang)
            # Go to that url and get our translated response
            async with session.get(url) as response:
                # Wait for our response and make it json so we can look at it like a dictionary
                request_result = await response.json()
                # Close response socket
                response.close()
        await session.close()
    # Get the result from the request result json
    translated = request_result['alternative_translations'][0]['alternative'][0]['word_postproc']
    # Return that
    return translated

async def translate_async(loop, sentances, tolang, fromlang='auto'):
    """Translate multiple sentances asyncronously."""
    coros = [get_translated_coroutine(loop, sentance, tolang, fromlang) for sentance in sentances]
    return await asyncio.gather(*coros)

def translate_sentances(sentances, tolang, fromlang='auto'):
    """Translate many sentances at once using the power of asyncronous code."""
    # Get asyncronous event loop
    event_loop = asyncio.get_event_loop()
    try:
        # Run the main function until it's done and get our translated sentances
        data = event_loop.run_until_complete(translate_async(event_loop, sentances, tolang, fromlang))
    finally:
        # Close the event loop no matter what
        event_loop.close()
    # Return translated sentances
    return data

def run():
##    print(translate(input('Translate words: '), input('To language: ')))
##    translate('Hello world!', 'fr', 'en')
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
                 'This is a test', 'Asyncronous code is faster yay']
    # Tell the person watching us what they are
    print(sentances)
    # We will be translating from english to french
    srclang = 'en'
    dstlang = 'fr'
    
    # Define two functions, one that translates our sentances one at a time (normaly)
    @Timed
    def without_async():
        print([translate(sentance, dstlang, srclang) for sentance in sentances])
    # and another that does it all asyncronously, both timed.
    @Timed
    def with_async():
        print(translate_sentances(sentances, dstlang, srclang))
    # Translate the sentances with both to prove asyncronous is better woo
    without_async()
    with_async()
    with_async()
    
    # Destroy the evidence!
    del without_async
    del with_async
    del Timed
    del time
    del wraps

if __name__ == '__main__':
    print('%s v%s\nProgrammed by %s.' % (__title__, __version__, __author__))
    run()
