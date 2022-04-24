#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TITLE DISCRIPTION

"Tools for lang conversion."

# Programmed by CoolCat467

__title__ = 'Convert'
__author__ = 'CoolCat467'
__version__ = '0.0.0'
__ver_major__ = 0
__ver_minor__ = 0
__ver_patch__ = 0

import json
##import asyncio

import translate
##from lang_globs import LANGUAGES, LANGCODES

def lang_to_json(lang_data: str) -> tuple[dict, dict]:
    "Fix lang data to be readable by json parser. Return data and comments."
    if not lang_data[-1]:
        lang_data = lang_data[:-1]
    lines = lang_data.splitlines()
    
    new_lines = []
    comments = {}
    
    for lidx, line in enumerate(lines):
        if '{' in line and '}' in line:
            indent = line.count('\t')*'\t'
            nline = line.replace('{', f'{{\n{indent}')
            nline = nline.replace('}', f'\n{indent}}}')
            data = nline.splitlines()
            ndata = []
            square = True
            for line in data[1:-1]:
                line = line.strip()
                if '=' in line:
                    square = False
                for value in line.split(','):
                    value = value.strip()
                    if not square:
                        key, value = value.split('=')
                        key = key.strip()
                        value = value.strip()
                        value = f'{key} = {value}'
                    ndata.append(f'{indent}\t{value}')
            nline = '\n'.join((data[0], ',\n'.join(ndata), data[-1]))
            new_lines += nline.splitlines()
            continue
        new_lines.append(line)
    lines, new_lines = new_lines, []
    
    nidx = 1
    while nidx < len(lines):
        nline = lines[nidx].strip()
        if not nline.startswith('--'):
            break
        nidx += 1
    square = '=' not in nline
    close_stack = [square]
    
    for lidx, line in enumerate(lines):
        idx = len(new_lines)
        if '--' in line:
            comment = line.split('--')[1].strip()
            comments[lidx] = comment
            continue
        elif line.strip() == '':
            comments[lidx] = ''
            continue
        elif '=' in line:
            key, value = line.split('=', 1)
            
            indent = key.count('\t')
            n_indent = '\t' * indent
            
            key = key.strip()
            value = value.strip()
            
            
            if key.startswith('[') and key.endswith(']'):
                key = key[1:-1]
                if close_stack[-1]:
##                    close_stack[-1] = False
##                    new_lines[idx-1] = new_lines[idx-1].replace('[', '{')
                    if value.startswith('"'):
                        value = value[1:]
                    if value.endswith(','):
                        value = value[:-1]
                    if value.endswith('"'):
                        value = value[:-1]
                    value += '$$$$'
                    new_lines.append(f'{n_indent}"{value}",')
                    continue
            elif value.startswith('{'):
                nidx = lidx+1
                while nidx < len(lines):
                    nline = lines[nidx].strip()
                    if not nline.startswith('--'):
                        break
                    nidx += 1
                square = '=' not in nline
                close_stack.append(square)
##                print(('-'*0xf, nline, square))
                if square:
                    value = value.replace('{', '[')
            line = f'{n_indent}"{key}": {value}'
        elif '}' in line:
            prev = new_lines[idx-1]
            if prev.endswith(','):
                new_lines[idx-1] = prev[:-1]
            if close_stack.pop():
                line = line.replace('}', ']')
        elif '{' in line:
##            print(line)
            nidx = lidx+1
            while nidx < len(lines):
                nline = lines[nidx].strip()
                if not nline.startswith('--'):
                    break
                nidx += 1
##            print(nline)
            square = '=' not in nline
##            print(square)
##            print('-'*0xf)
            close_stack.append(square)
            if square:
                line = line.replace('{', '[')
        new_lines.append(line)
##    last_comment = max(comments)
##    if not comments[last_comment]:
##        del comments[last_comment]
##    print('\n'.join(new_lines))
    return json.loads('\n'.join(new_lines)), comments

def dict_to_lang(data: dict, comments: dict={}) -> str:
    "Convert data and comments to MineOS .lang data"
    json_data = json.dumps(data, ensure_ascii=False,
                           indent='\t', separators=(',', ' = '))
    new_lines = []
    for line in json_data.splitlines():
        idx = len(new_lines)
        
        indent = line.count('\t')*'\t'
        
        if idx in comments:
            comment = comments[idx]
            if comment:
                new_lines.append(f'{indent}-- {comment}')
            else:
                new_lines.append('')
        
        line = line.replace('[', '{')
        line = line.replace(']', '}')
        
        if ' = ' in line:
            key, value = line.split(' = ', 1)
            key = key.strip()
            
            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
            
            if key.isdigit():
                key = f'[{key}]'
            
            line = f'{indent}{key} = {value}'
        elif '}' in line:
            prev = new_lines[idx-1]
            if not prev.endswith(','):
                new_lines[idx-1] = prev+','
        elif '$$$$' in line:
            value = line.strip()
            line = f'{indent}[0] = {value}'
        new_lines.append(line)
##    print('\n'.join(new_lines))
    return '\n'.join(new_lines)



def update_comment_positions(original_pos: dict, new_data: dict, old_data: dict):
    "Update comment positions"
    for section, section_block in new_data.items():
        
    
    return original_pos

def read_lang_file(filepath: str) -> tuple[dict, dict]:
    "Read MineOS .lang file"
    with open(filepath, 'r', encoding='utf-8') as fp:
        fdata = fp.read()
    return lang_to_json(fdata)

def write_lang_file(filepath: str, data: dict, comments: dict) -> None:
    "Write MineOS .lang file"
    with open(filepath, 'w', encoding='utf-8') as fp:
        fp.write(dict_to_lang(data, comments))

def partquotes(text: str, item: int, quotes: str='"') -> str:
    "Return item th part of text that is enclosed in quotes"
    return text.split(quotes)[2*item+1]

def dict_to_list(data: dict) -> tuple[list, list]:
    keys, values = [], []
    for key, value in data.items():
        if isinstance(key, int):
            key = f'{key}?'
        if isinstance(value, dict):
            nd = [(f'{key}${k}$', v) for k, v in zip(*dict_to_list(value))]
            for k, v in nd:
##                if not isinstance(k, int):
##                    k += 'v'
                keys.append(k)
                values.append(v)
        elif isinstance(value, list):
            nd = {f'{key}#{i}?#': v for i, v in enumerate(value)}
            for k, v in zip(*dict_to_list(nd)):
##                if not isinstance(k, int):
##                    k += 'v'
                keys.append(k)
                values.append(v)
        else:
            keys.append(key)
            values.append(value)
##    print(data)
##    print((keys, values))
    return keys, values#list(map(str, keys)), list(map(str, values))

def list_to_dict(keys: list, values: list) -> dict:
    "Convert split lists of compiled keys and values back into dictionary"
    def unwrap_keys(key_data, set_val, data):
##        print(f'{key_data = }')
        pidx = 0
        while key_data:
            char_key_data = str(key_data)
            if '$' in char_key_data or '#' in char_key_data:
                found = 0
                for idx, char in enumerate(char_key_data):
                    if char in {'$', '#'}:
                        if found == (pidx*2):
                            break
                        found += 1
##                print(f'{pidx=}')
                parent = key_data[:idx]
                next_layer = partquotes(key_data, 0, char)
                
                parent_val, next_layer_val = parent, next_layer
                if parent_val.endswith('?'):
                    parent_val = int(parent_val[:-1])
                if next_layer_val.endswith('?'):
                    next_layer_val = int(next_layer_val[:-1])
                
##                print(f'{parent_val=}')
##                print(f'{next_layer_val=}')
                if char == '#':#list index
                    if isinstance(data, dict):
                        if not parent_val in data:
                            data[parent_val] = []
                    else:
                        if parent_val+1 > len(data):
                            data.append([])
                else:#dict index
                    if isinstance(data, dict):
                        if not parent_val in data:
                            data[parent_val] = {}
                    else:
                        if parent_val+1 > len(data):
                            data.append({})
                
##                print((char_key_data, parent, next_layer, set_val))
##                print('-'*0xf)
##                
##                print(key_data)
                
                key_data = key_data[idx+len(next_layer)+2:]
                if key_data:
##                    print(key_data)
##                    print(next_layer)
##                    print(char)
##                    if char == '#':
##
##                    print(key_data)
                    key_data = next_layer+key_data
##                    print((data[parent_val], next_layer, key_data))
                    unwrap_keys(key_data, set_val, data[parent_val])
                    key_data = ''
##                    pidx = 0
                else:
                    unwrap_keys(next_layer, set_val, data[parent_val])
##                print()
            elif isinstance(data, list):
                data.append(set_val)
                key_data = ''
            else:
                if isinstance(key_data, str) and key_data.endswith('?'):
                    key_data = int(key_data[:-1])
                data[key_data] = set_val
                key_data = ''
            pidx += 1
##            print(data)
    global data
    data = {}
    for k, v in zip(keys, values):
        unwrap_keys(k, v, data)
    return data

##k, v = dict_to_list({'cat': {3: '5', 7:'9', 4: [4, 3, 3]}, 'meep': [1, 2, [2, 3, 4]]})
##print((k, v))
##print(list_to_dict(k, v))

async def translate_file(data: dict, loop, to_lang: str, src_lang: str='auto') -> dict:
    "Translate an entire file."
    keys, sentances = dict_to_list(data)
##    name_order = tuple(sorted(data))
##    sentances = [data[key] for key in name_order]
    results = await translate.translate_async(loop, sentances, to_lang, src_lang, 1.5)
##    zip(name_order, results)
    return list_to_dict(keys, results)

##async def async_run(loop):
##    "Async entry point"
##    data, comments = read_lang_file('English.lang')
##    new_data = await translate_file(data, loop, 'fr', 'en')
##    lang = dict_to_lang(new_data, comments)
####    data, comments = read_lang_file('files.cfg')
####    print(comments)
##    print(lang)
##
##def run():
##    "Main entry point"
##    loop = asyncio.new_event_loop()
##    try:
##        loop.run_until_complete(async_run(loop))
##    finally:
##        loop.close()

if __name__ == '__main__':
    print(f'{__title__} v{__version__}\nProgrammed by {__author__}.\n')
##    run()
