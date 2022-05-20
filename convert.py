#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Conversion tools

"Tools for lang conversion."

# Programmed by CoolCat467

__title__ = 'Convert'
__author__ = 'CoolCat467'
__version__ = '1.0.0'
__ver_major__ = 1
__ver_minor__ = 0
__ver_patch__ = 0

import json

import translate

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
    
    section = []
    
    for lidx, line in enumerate(lines):
        idx = len(new_lines)
        
        if section:
            offset = lidx - section[-1][1]
            path = '/'.join(s[0] for s in section)
            
            if '--' in line:
                comment = line.split('--')[1].strip()
                
                if not path in comments:
                    comments[path] = {}
                
                comments[path][offset] = comment
                continue
            elif line.strip() == '':
                if not path in comments:
                    comments[path] = {}
                
                comments[path][offset] = ''
                continue
        if '=' in line:
            key, value = line.split('=', 1)
            
            indent = key.count('\t')
            n_indent = '\t' * indent
            
            key = key.strip()
            value = value.strip()
                        
            if key.startswith('[') and key.endswith(']'):
                key = key[1:-1]
                if close_stack[-1]:
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
                section.append((key, lidx))
                nidx = lidx+1
                while nidx < len(lines):
                    nline = lines[nidx].strip()
                    if not nline.startswith('--'):
                        break
                    nidx += 1
                square = '=' not in nline
                close_stack.append(square)
                if square:
                    value = value.replace('{', '[')
            line = f'{n_indent}"{key}": {value}'
        elif '}' in line:
            prev = new_lines[idx-1]
            if prev.endswith(','):
                new_lines[idx-1] = prev[:-1]
            if close_stack.pop():
                line = line.replace('}', ']')
            section.pop()
        elif '{' in line:
            section.append(('null', lidx))
            nidx = lidx+1
            while nidx < len(lines):
                nline = lines[nidx].strip()
                if not nline.startswith('--'):
                    break
                nidx += 1
            square = '=' not in nline
            close_stack.append(square)
            if square:
                line = line.replace('{', '[')
        new_lines.append(line)
    return json.loads('\n'.join(new_lines)), comments

def dict_to_lang(data: dict, comments: dict={}) -> str:
    "Convert data and comments to MineOS .lang data"
    json_data = json.dumps(data, ensure_ascii=False,
                           indent='\t', separators=(',', ' = '))
    new_lines = []
    section = []
    for line in json_data.splitlines():
        idx = len(new_lines)
        
        indent = line.count('\t')*'\t'
        
        line = line.replace('[', '{')
        line = line.replace(']', '}')
        
        if '{' in line:
            key = 'null'
            if ' = ' in line:
                key = line.split(' = ', 1)[0].strip()
                if key.startswith('"') and key.endswith('"'):
                    key = key[1:-1]
            section.append((key, idx))
        
        if '}' in line:
            path = '/'.join(s[0] for s in section)
            sec_start = section.pop()[1]
            if path in comments:
                for offset, comment in comments[path].items():
                    pos = sec_start + offset
                    if comment:
                        comment = f'{indent}\t-- {comment}'
                    else:
                        comment = '\t'+indent
                    new_lines.insert(pos, comment)
            prev = new_lines[-1]
            if not prev.endswith(','):
                new_lines[-1] = prev+','
        
        if ' = ' in line:
            key, value = line.split(' = ', 1)
            key = key.strip()
            
            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
            if key.isdigit():
                key = f'[{key}]'
            
            line = f'{indent}{key} = {value}'
        
        if '$$$$' in line:
            value = line.strip()
            line = f'{indent}[0] = {value}'
        new_lines.append(line)
    return '\n'.join(new_lines)

def split(p):
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
everything after the final slash.  Either part may be empty."""
    path = p.split('/')
    return '/'.join(path[:-1]), path[-1]

def section_to_walk(section: list) -> tuple:
    "Return folder and files from section"
    dirs = {}
    for full_path in section:
        path, filename = split(full_path)
        if not path in dirs:
            dirs[path] = []
        dirs[path].append(filename)
    return tuple(dirs.items())

def update_comment_positions(original_pos: dict, new_data: dict, old_data: dict):
    "Update comment positions"
    # Get json of files
    old_json = json.dumps(old_data, indent='\t').splitlines()#.replace('\t', '').splitlines()
    new_json = json.dumps(new_data, indent='\t').splitlines()#.replace('\t', '').splitlines()
    
    new_comments = {}
    # For each section in the original comments data
    for section in (f'null/{x}' for x in old_data if f'null/{x}' in original_pos):
        # Reads include comment, so have to keep track of coments read.
        read_offset = 0
        
        # Make predictions of guess where it is in new version more accurate
        sec_add = 0
        
        # Remove null/ from name
        name = section[5:]
        # If sections of data are not the same
        if new_data[name] != old_data[name]:
            # Find start of section in new and old json
            start = f'\t"{name}": ['
            obs = old_json.index(start)-1
            nbs = new_json.index(start)-1
            n_end = new_json.index('\t]')+1
            # Initialize section
            new_comments[section] = {}
            # For each offset in the comments
            for offset in sorted(original_pos[section]):
                # Find line comment lives on
                old_comment = old_json[obs+offset-read_offset]
                
                # Find start to look for same line in new
                start = nbs+offset-read_offset+sec_add
                start = max(nbs, start)
                
                # Find old comment position in new json
                new_pos = new_json.index(old_comment, start, n_end)
                
                # Cumulative additions
                sec_add = max(sec_add, new_pos - start)
                
                # New position needs to be offset as well
                new_pos += read_offset
                
                # Update offset
                read_offset += 1
                
                # Record new comment
                new_comments[section][new_pos-nbs] = original_pos[section][offset]
    return new_comments

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
                keys.append(k)
                values.append(v)
        elif isinstance(value, list):
            nd = {f'{key}#{i}?#': v for i, v in enumerate(value)}
            for k, v in zip(*dict_to_list(nd)):
                keys.append(k)
                values.append(v)
        else:
            keys.append(key)
            values.append(value)
    return keys, values

def list_to_dict(keys: list, values: list) -> dict:
    "Convert split lists of compiled keys and values back into dictionary"
    def unwrap_keys(key_data, set_val, data):
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
                parent = key_data[:idx]
                next_layer = partquotes(key_data, 0, char)
                
                parent_val, next_layer_val = parent, next_layer
                if parent_val.endswith('?'):
                    parent_val = int(parent_val[:-1])
                if next_layer_val.endswith('?'):
                    next_layer_val = int(next_layer_val[:-1])
                
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
                
                key_data = key_data[idx+len(next_layer)+2:]
                if key_data:
                    key_data = next_layer+key_data
                    unwrap_keys(key_data, set_val, data[parent_val])
                    key_data = ''
                else:
                    unwrap_keys(next_layer, set_val, data[parent_val])
            elif isinstance(data, list):
                data.append(set_val)
                key_data = ''
            else:
                if isinstance(key_data, str) and key_data.endswith('?'):
                    key_data = int(key_data[:-1])
                data[key_data] = set_val
                key_data = ''
            pidx += 1
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
    results = await translate.translate_async(loop, sentances, to_lang, src_lang, 1.5)
    return list_to_dict(keys, results)

def translate_file_copy_paste(data: dict) -> dict:
    "Translate an entire file by creating text to paste into translator and reading the response"
    keys, sentances = dict_to_list(data)
    encoded = ' # '.join(sentances)
    print()
    print(encoded)
    print()
    raw_results = input('Paste result here: ')
    results = raw_results.split(' # ')
    return list_to_dict(keys, results)

if __name__ == '__main__':
    print(f'{__title__} v{__version__}\nProgrammed by {__author__}.\n')
