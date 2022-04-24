#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TITLE DISCRIPTION

"Docstring"

# Programmed by CoolCat467

__title__ = 'TITLE'
__author__ = 'CoolCat467'
__version__ = '0.0.0'
__ver_major__ = 0
__ver_minor__ = 0
__ver_patch__ = 0

import os
import asyncio
import json
import base64
import time

import aiohttp

import convert
import languages
import timeutils

def raw_github_address(user: str, repo: str, branch: str, path: str) -> str:
    "Get raw github user content url of a specific file."
##    return f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}'
    return f'http://api.github.com/repos/{user}/{repo}/contents/{path}'

def mineos_url(path: str) -> str:
    "Return raw github address to path from MineOS repository."
    return raw_github_address('IgorTimofeev', 'MineOS', 'master', path)

async def download_coroutine(session, url: str) -> bytes:
    "Return the sentance translated, asyncronously."
    # Go to the url and get response
    async with session.get(url) as response:
        # Wait for our response
        message = await response.content.read()
        if 'x-Ratelimit-Remaining' in response.headers:
            still = response.headers['X-RateLimit-Reset']
            print(f'Requests Remaining: {still}')
        if 'X-RateLimit-Reset' in response.headers:
                delay = round(int(response.headers['X-RateLimit-Reset']) - time.time())
                print(f'Rate limiting resets in {timeutils.format_time(delay)}')
        if not response.ok:
            raise IOError(f'{response.url} : [{response.status}] [{response.reason}]: {message}')
        return message

def ensure_folder_exists(new_filename: str) -> None:
    "Ensure folder chain for new filename exists."
    new_filename = os.path.abspath(new_filename)
    path = (os.path.split(new_filename)[0]).split(os.path.sep)
    for l in range(2, len(path)+1):
        new_path = os.path.sep.join(path[:l])
        if not os.path.exists(new_path):
            os.mkdir(new_path)

async def download_file(path: str, cache_dir: str, session) -> str:
    "Download file at path from MineOS repository."
    real_path = os.path.join(cache_dir, *path.split('/'))
    if not os.path.exists(real_path):
        ensure_folder_exists(real_path)
        print(f'GET {path}')
        response = await download_coroutine(session, mineos_url(path))
        j_resp = json.loads(response)
        data = base64.b64decode(j_resp['content'])
        with open(real_path, 'wb') as file:
            file.write(data)
        return data.decode('utf-8')
    print(f'Loaded {path} from cache')
    with open(real_path, 'r', encoding='utf-8') as file:
        return file.read()

async def download_lang(path: str, cache_dir: str, session) -> tuple[dict, dict]:
    "Download file from MineOS repository and decode as lang file. Return dict and commetns"
    return convert.lang_to_json(await download_file(path, cache_dir, session))

def commonpath(paths: list) -> str:
    "Given a sequence of path names, returns the longest common sub-path."
    sub_paths = [p.split('/') for p in paths]
    m_len = max(map(len, sub_paths))
    long_sub = []
    c_long = -1
    while c_long < m_len:
        check = sub_paths[0][c_long+1]
        for p in sub_paths[1:]:
            if p[c_long+1] != check:
                return '/'.join(long_sub)
        c_long += 1
        long_sub.append(check)
    return '/'.join(long_sub)

def split(p):
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
everything after the final slash.  Either part may be empty."""
    path = p.split('/')
    return '/'.join(path[:-1]), path[-1]

def section_to_walk(section: list) -> tuple:
    dirs = {}
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

async def async_run(loop):
    "Async entry point"
    
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
    
    here_folder = os.path.split(__file__)[0]
    base_lang = os.path.join(here_folder, 'Upload')
    cache_folder = os.path.join(here_folder, 'cache')
    
    ignore_languages = {'chinese (traditional)', }
    convert_name = {'zh-cn': 'chinese'}
    
    timeout_obj = aiohttp.ClientTimeout(10)
    async with aiohttp.ClientSession(loop=loop, timeout=timeout_obj,
##                                     trace_configs=[trace_config]
                                     ) as session:
        print('\nGettting files...')
        files, file_comments = await download_lang('Installer/Files.cfg', cache_folder, session)
        orig_files = files.copy()
        search = []
        for section, data in files.items():
            for entry in data:
                if not isinstance(entry, str):
                    continue
                if entry.endswith('English.lang'):
                    search.append(section)
                    break
        print(f'\nSections with .lang files: {", ".join(search)}\n')
        for section in search:
            lang_files = [f for f in files[section] if isinstance(f, str) and f.endswith('.lang')]
            if not lang_files:
                continue
            print('#'*0x20+section+'#'*0x20)
            for folder, exists in section_to_walk(lang_files):                
                handled_langs = [(f.split('.')[0]).lower() for f in exists]
                if not handled_langs:
                    continue
                last_handled = folder+'/'+handled_langs[-1].title()+'.lang'
                handled_langs = set(handled_langs)
                handled_langs |= ignore_languages
                
                unhandled = [v for k, v in languages.LANGCODES.items() if not k in handled_langs]
                
                english, comments = await download_lang(f'{folder}/English.lang',
                                                        cache_folder, session)
                
                real_folder = os.path.sep.join(folder.split('/'))
                base_group = os.path.join(base_lang, real_folder)
                total = len(unhandled)
                print(f'\n{total} languages do not exist, translating them now!')
                insert_start = files[section].index(last_handled)
                for idx, to_lang in enumerate(unhandled):
                    name = convert_name.get(to_lang,
                                            languages.LANGUAGES[to_lang]).title()
                    
                    fname = name.replace(' ', '_')
                    fname = fname.replace('(', '').replace(')', '')
                    filename = os.path.join(base_group, f'{fname}.lang')
                    files[section].insert(insert_start+idx, f'{folder}/{fname}.lang')
                    
                    if not os.path.exists(filename):
                        print(f'{idx+1}/{total}: {name} -> {fname}.lang')
                        new_lang = await convert.translate_file(english, loop, to_lang, 'en')
                        ensure_folder_exists(filename)
                        convert.write_lang_file(filename, new_lang, comments)
                print('\n'+'#'*0xf+'Done with folder'+'#'*0xf)
    print('\nLanguages have been translated and saved to upload folder!')
    print('Writing Installer/Files.cfg...')
    file_list_filename = os.path.join(base_lang, 'Installer', 'Files.cfg')
    file_comments = convert.update_comment_positions(file_comments, orig_files, files)
    ensure_folder_exists(file_list_filename)
    convert.write_lang_file(file_list_filename, files, file_comments)
    print('Done!')

def run():
    "Main entry point"
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(async_run(loop))
    finally:
        loop.close()

if __name__ == '__main__':
    print(f'{__title__} v{__version__}\nProgrammed by {__author__}.')
    run()
