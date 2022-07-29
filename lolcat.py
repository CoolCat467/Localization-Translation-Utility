#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Lolcat Translator - Scrape lolcat translation website

"Lolcat Translator"

# Programmed by CoolCat467

__title__ = 'Lolcat Scraper'
__author__ = 'CoolCat467'
__version__ = '0.0.0'

from typing import Any, Optional, Sequence

from html.parser import HTMLParser

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
    
    def handle_starttag(self, tag_type: str, attrs: list) -> None:
        "Set found to True if tag type and id matches search"
        if tag_type == self.search_tag_type:
            creation = dict(attrs)
            if not 'id' in creation:
                return
            if creation['id'] == self.search_id:
                self.found = True
    
    def handle_data(self, value: str):
        "Set value to value if currently handling target"
        if self.found:
            self.value = value
    
    def handle_endtag(self, tag_type: str) -> None:
        "Set found to false if end of search tag"
        if tag_type == self.search_tag_type and self.found:
            self.found = False

def translate_sentance(sentance: str) -> str:
    "Translate sentance"
    browser = mechanicalsoup.StatefulBrowser()
    browser.open("https://funtranslations.com/lolcat")
    browser.select_form('form#textform')
    browser["text"] = sentance
    response = browser.submit_selected()
    
    p = ResponseParser('span', 'lolcat')
    p.feed(response.text)
    p.close()
    
    value = p.value
    if value.endswith(' ') and not sentance.endswith(' '):
        value = value[:-1]
    
    while ' Srsly ' in value:
        index = value.index(' Srsly ')
        if value[index - 1] == ',':
            value = value[:index-1] + value[index:]
            index -= 1
        value = value[:index] + value[index+7:]
    
    if sentance[0].isupper():
        value = value[0].upper() + value[1:]
    
    return value.replace('.  ', '. ')

def translate_block(sentances: list[str]) -> str:
    "Translate sentances in bulk"
    sep = '^&^'
    block = sep.join(sentances)
    response = translate_sentance(block).split(sep)
    result = []
    for orig, new in zip(sentances, response):
        if orig[0].isupper():
            new = new[0].upper() + new[1:]
        result.append(new)
##        print(f'{orig!r} -> {new!r}')
    return result

def translate_file(english: dict) -> dict:
    "Translate an entire file."
    keys, sentances = extricate.dict_to_list(english)
    
    results = translate_block(sentances)
    
    for old, new in zip(enumerate(sentances), results):
        idx, orig = old
        if new is None or not isinstance(old, str):
            results[idx] = orig
            continue
        if orig.endswith(' ') and not new.endswith(' '):
            results[idx] = new + ' '
    return extricate.list_to_dict(keys, results)

def run():
    "Run test of module"
    text = [
        'This is hearsay!',
        'I am the way, the truth, and the life. No one comes to God except through me.',
        'You understand, mechanical hands are the ruler of everything',
        'Do you swear to say the complete truth, the whole truth, and nothing but the truth?',
    ]
    print(text)
    print(translate_block(text))
    

if __name__ == '__main__':
    print(f'{__title__}\nProgrammed by {__author__}.\n')
    run()
