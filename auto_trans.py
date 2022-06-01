#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Auto Translate localizations for MineOS

"Auto Translate localizations for MineOS"

# Programmed by CoolCat467

__title__ = 'Auto_Trans'
__author__ = 'CoolCat467'
__version__ = '2.0.0'
__ver_major__ = 2
__ver_minor__ = 0
__ver_patch__ = 0

import os
import json
import base64
import time
import copy

import trio
import httpx

import translate
import convert
import languages
import timeutils

def raw_github_address(user: str, repo: str, branch: str, path: str) -> str:
    "Get raw github user content url of a specific file."
##    return f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}'
    return f'https://api.github.com/repos/{user}/{repo}/contents/{path}'

def mineos_url(path: str) -> str:
    "Return raw github address to path from MineOS repository."
    return raw_github_address('IgorTimofeev', 'MineOS', 'master', path)

async def download_coroutine(client: httpx.AsyncClient, url: str) -> bytes:
    "Return the sentance translated, asyncronously."
    # Go to the url and get response
    response = await client.get(url, follow_redirects=True)
    if 'x-Ratelimit-Remaining' in response.headers:
        still = response.headers['X-RateLimit-Reset']
        print(f'Requests Remaining: {still}')
    if 'X-RateLimit-Reset' in response.headers:
        delay = round(int(response.headers['X-RateLimit-Reset']) - time.time())
        print(f'Rate limiting resets in {timeutils.format_time(delay)}')
    if not response.is_success:
        response.raise_for_status()
    # Wait for our response
    return await response.aread()

def ensure_folder_exists(new_filename: str) -> None:
    "Ensure folder chain for new filename exists."
    new_filename = os.path.abspath(new_filename)
    path = (os.path.split(new_filename)[0]).split(os.path.sep)
    for i in range(2, len(path)+1):
        new_path = os.path.sep.join(path[:i])
        if not os.path.exists(new_path):
            os.mkdir(new_path)

async def download_file(path: str, cache_dir: str, client: httpx.AsyncClient) -> str:
    "Download file at path from MineOS repository."
    real_path = os.path.join(cache_dir, *path.split('/'))
    if not os.path.exists(real_path):
        ensure_folder_exists(real_path)
        print(f'GET {path}')
        response = await download_coroutine(client, mineos_url(path))
        j_resp = json.loads(response)
        data = base64.b64decode(j_resp['content'])
        with open(real_path, 'wb') as file:
            file.write(data)
        await trio.sleep(1)
        return data.decode('utf-8')
    print(f'Loaded {path} from cache')
    with open(real_path, 'r', encoding='utf-8') as file:
        return file.read()

async def download_lang(path: str, cache_dir: str, client: httpx.AsyncClient) -> tuple[dict, dict]:
    "Download file from MineOS repository and decode as lang file. Return dict and commetns"
    return convert.lang_to_json(await download_file(path, cache_dir, client))

def commonpath(paths: list) -> str:
    "Given a sequence of path names, returns the longest common sub-path."
    sub_paths = [p.split('/') for p in paths]
    m_len = max(map(len, sub_paths))
    long_sub: list[str] = []
    c_long = -1
    while c_long < m_len:
        check = sub_paths[0][c_long+1]
        for path in sub_paths[1:]:
            if path[c_long+1] != check:
                return '/'.join(long_sub)
        c_long += 1
        long_sub.append(check)
    return '/'.join(long_sub)

def split(path: str) -> tuple[str, str]:
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
everything after the final slash.  Either part may be empty."""
    data = path.split('/')
    return '/'.join(data[:-1]), data[-1]

def section_to_walk(section: list) -> tuple:
    "Return folder and files from section"
    dirs: dict[str, list[str]] = {}
    for full_path in section:
        path, filename = split(full_path)
        if not path in dirs:
            dirs[path] = []
        dirs[path].append(filename)
    return tuple(dirs.items())

##def find_groups(walk):
##    dirs = {}
##    go = False
##    for dirpath, filenames in walk:
##        from_base = commonpath(('/', dirpath))
##        entry = dirpath[len(from_base):]
##        
##        follow = entry.split('/')
##        if len(follow) > 1:
##            if not follow[0] in dirs:
##                dirs[follow[0]] = {}
##            part = dirs[follow[0]]
##            for link in follow[1:]:
##                if not link in part:
##                    part[link] = {}
##                part = part[link]
##            part[''] = filenames
##        elif entry:
##            dirs[entry] = {'': filenames}
##        else:
##            dirs[entry] = filenames
##    return dirs

async def translate_file(trans_coro, file: tuple[dict, dict], lang_data: list[tuple[str, str]]) -> None:
    "Translate a file for all languages in lang_data and save as filename from data."
    # English and comments is file
    # to_lang and filename is each entry in lang_data
    total = len(lang_data)
    english, comments = file
    
    async def translate_file_coro(to_lang: str, filename: str) -> None:
        "Translate file from english to to_lang, save as filename."
        new_lang = await trans_coro(english, to_lang)
        print(to_lang.title())
        convert.write_lang_file(filename, new_lang, comments)
    
    async with trio.open_nursery() as nursery:
        for to_lang, filename in lang_data:
            nursery.start_soon(translate_file_coro, to_lang, filename)

async def abstract_translate(client: httpx.AsyncClient,
                             base_lang: str, cache_folder: str,
                             get_unhandled,
                             trans_coro,
                             ) -> None:
    "Main translate"
    
    ignore_languages = {'chinese (traditional)', }
    convert_name = {'zh-cn': 'chinese'}
    
    print('\nGettting files...')
    files, file_comments = await download_lang('Installer/Files.cfg',
                                               cache_folder, client)
    # Get true copy
    orig_files = copy.deepcopy(files)
    
    search = []
    for section, data in files.items():
        for entry in data:
            if isinstance(entry, str) and entry.endswith('English.lang'):
                search.append(section)
                break
    
    print(f'\nSections with English.lang files: {", ".join(search)}\n')
    
    new_files = 1
    
    for section in search:
        lang_files = [f for f in files[section] if isinstance(f, str) and f.endswith('.lang')]
        if not lang_files:
            continue
        print('#'*0x20+section+'#'*0x20)
        for folder, exists in section_to_walk(lang_files):                
            handled_langs = {(f.split('.')[0]).lower() for f in exists}
            if not handled_langs:
                continue
            last_handled = folder+'/'+exists[-1].split('.')[0].title()+'.lang'
            handled_langs |= ignore_languages
            
            unhandled = get_unhandled(handled_langs, folder)
            
            if not unhandled:
                print('All translations exist for this folder, skipping.')
                continue
            
            english, comments = await download_lang(f'{folder}/English.lang',
                                                    cache_folder, client)
            
            real_folder = os.path.sep.join(folder.split('/'))
            base_group = os.path.join(base_lang, real_folder)
            total = len(unhandled)
            print(f'\n{total} languages do not exist, translating them now!')
            insert_start = files[section].index(last_handled)
            
            lang_data = []
            
            for idx, to_lang in enumerate(unhandled):
                name = convert_name.get(to_lang, to_lang).title()
                
                fname = name.replace(' ', '_')
                fname = fname.replace('(', '').replace(')', '')
                filename = os.path.join(base_group, f'{fname}.lang')
                files[section].insert(insert_start+idx, f'{folder}/{fname}.lang')
                
                if not os.path.exists(filename):
##                if True:
                    ensure_folder_exists(filename)
                    lang_data.append((to_lang, filename))
                new_files += 1
            
            await translate_file(trans_coro, (english, comments), lang_data)
            print('\n'+'#'*0xf+'Done with folder'+'#'*0xf)
    print('\nLanguages have been translated and saved to upload folder!')
    print('Writing Installer/Files.cfg...')
    file_list_filename = os.path.join(base_lang, 'Installer', 'Files.cfg')
    file_comments = convert.update_comment_positions(file_comments, files, orig_files)
    ensure_folder_exists(file_list_filename)
    convert.write_lang_file(file_list_filename, files, file_comments)
    print(f'Done! {new_files} new files created.')

@timeutils.async_timed
async def translate_main(client) -> None:
    "Translate with google translate"
    
    here_folder = os.path.split(__file__)[0]
    base_lang = os.path.join(here_folder, 'Upload')
    cache_folder = os.path.join(here_folder, 'cache')
    
    def get_unhandled(handled: set, folder: str) -> list:
##        return [v for k, v in languages.LANGCODES.items() if not k in handled]
        return [k for k in languages.LANGCODES if not k in handled]
##        return ['greek']
    
    async def trans_coro(english: dict,
                         to_lang: str) -> dict:
        code = languages.LANGCODES[to_lang]
        return await convert.translate_file(english, client, code, 'en')
    
    await abstract_translate(client, base_lang, cache_folder,
                             get_unhandled, trans_coro)

@timeutils.async_timed
async def translate_new_value(client, key: str, folder: str) -> None:
    "Translate with google translate"
    
    here_folder = os.path.split(__file__)[0]
    base_lang = os.path.join(here_folder, 'Upload')
    cache_folder = os.path.join(here_folder, 'cache')
    
    def get_unhandled(handled: set, lang_folder: str) -> list:
        if lang_folder == folder:
            return handled.difference({'chinese (traditional)',
                                       'english',
                                       'lolcat'})
        return []
    
    async def trans_coro(english: dict,
                         to_lang: str) -> dict:
        fname = to_lang.replace(' ', '_')
        fname = fname.replace('(', '').replace(')', '').title()
        filename = f'{folder}/{fname}.lang'
##        print(f'\t\t-- {to_lang}')
        
        data = (await download_lang(filename, cache_folder, client))[0]
        
        if to_lang == 'chinese':
            to_lang += ' (traditional)'
        
        code = languages.LANGCODES[to_lang]
        
        values = await translate.translate_async(client, [english[key]], code, 'en')
##        return {key: values[0]}
##        print((data[key], values[0]))
        data[key] = values[0]
        return data
    
    await abstract_translate(client, base_lang, cache_folder,
                             get_unhandled, trans_coro)

async def translate_lolcat(client) -> None:
    "Translate with website"
    # https://funtranslations.com/lolcat
    
    here_folder = os.path.split(__file__)[0]
    base_lang = os.path.join(here_folder, 'Upload')
    cache_folder = os.path.join(here_folder, 'cache')
    
    def get_unhandled(handled: set, folder: str) -> list:
        return ['lolcat'] if not 'lolcat' in handled else []
    
    async def trans_coro(english: dict,
                         to_lang: str) -> dict:
        return convert.translate_file_copy_paste(english)
    
    await abstract_translate(client, base_lang, cache_folder,
                             get_unhandled, trans_coro)

async def async_run() -> None:
    "Async entry point"
    async with httpx.AsyncClient(http2 = True) as client:
##        await translate_main(client)
        await translate_new_value(client, 'screenPreciseMode', 'Applications/Settings.app/Localizations')

def run() -> None:
    "Main entry point"
    trio.run(async_run)

if __name__ == '__main__':
    print(f'{__title__} v{__version__}\nProgrammed by {__author__}.')
    run()
