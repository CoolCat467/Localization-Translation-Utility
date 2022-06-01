#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Conversion tools

"Tools for lang conversion."

# Programmed by CoolCat467

__title__ = 'Convert'
__author__ = 'CoolCat467'
__version__ = '1.2.0'
__ver_major__ = 1
__ver_minor__ = 2
__ver_patch__ = 0

import json

import translate

# lintcheck: too-many-locals (R0914): Too many local variables (25/15)
def lang_to_json(lang_data: str) -> tuple[dict, dict]:
    "Fix lang data to be readable by json parser. Return data and comments."
    if not lang_data[-1]:
        lang_data = lang_data[:-1]
    lines = lang_data.splitlines()
    
    new_lines = []
    comments: dict[str, dict[int, str]] = {}
    
    for lidx, line in enumerate(lines):
        if '{' in line and '}' in line:
            n_indent = line.count('\t')*'\t'
            nline = line.replace('{', f'{{\n{n_indent}')
            nline = nline.replace('}', f'\n{n_indent}}}')
            data = nline.splitlines()
            ndata = []
            square = True
            for dline in data[1:-1]:
                dline = dline.strip()
                if '=' in dline:
                    square = False
                for value in dline.split(','):
                    value = value.strip()
                    if not square:
                        key, value = value.split('=')
                        key = key.strip()
                        value = value.strip()
                        value = f'{key} = {value}'
                    ndata.append(f'{n_indent}\t{value}')
            nline = '\n'.join((data[0], ',\n'.join(ndata), data[-1]))
            new_lines += nline.splitlines()
            continue
        new_lines.append(line)
    lines, new_lines = new_lines, []
    
    section = [('null', 0)]
    close_stack: list[bool] = []
    
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
            if line.strip() == '':
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
            
            if key.startswith('[') and key.endswith(']') and close_stack[-1]:
                key = key[1:-1]
                com = False
                strng = False
                if value.endswith(','):
                    value = value[:-1]
                    com = True
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                    strng = True
                value += '$$$$'
                if strng:
                    value = f'"{value}"'
                if com:
                    value += ','
                
                new_lines.append(f'{n_indent}{value}')
                continue
            if value.startswith('{'):
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
                line = line.replace('}', ']', 1)
            section.pop()
        elif '{' in line:
            section.append(('dict', lidx))
            nidx = lidx+1
            while nidx < len(lines):
                nline = lines[nidx].strip()
                if not nline.startswith('--'):
                    break
                nidx += 1
            square = '=' not in nline
            close_stack.append(square)
            if square:
                line = line.replace('{', '[', 1)
        new_lines.append(line)
##    print('\n'.join(new_lines))
##    print(comments)
    return json.loads('\n'.join(new_lines)), comments

# lintcheck: too-many-locals (R0914): Too many local variables (16/15)
def dict_to_lang(data: dict, comments: dict) -> str:
    "Convert data and comments to MineOS .lang data"
    json_data = json.dumps(data, ensure_ascii=False,
                           indent='\t', separators=(',', ' = '))
    new_lines: list[str] = []
    section: list[tuple[str, int]] = [('null', 0)]
    for line in json_data.splitlines():
        idx = len(new_lines)
        
        indent = line.count('\t')*'\t'
        
##        line = line.replace('[', '{', 1)
##        line = line.replace(']', '}', 1)
        
        if ' = ' in line and line.split(' = ')[1].strip() == '[' or line.strip() == '[':
            line = line.replace('[', '{', 1)
        if line.strip() in {'],', ']'}:
            line = line.replace(']', '}', 1)
        
        if '{' in line:
            key = 'dict'
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
                    if pos >= len(new_lines):
                        indent = ''
                    else:
                        indent = new_lines[pos].count('\t')*'\t'
                    if comment:
                        comment = f'{indent}-- {comment}'
                    else:
                        comment = indent
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
            value = line.strip().replace('$$$$', '', 1)
            line = f'{indent}[0] = {value}'
        new_lines.append(line)
    
    path = '/'.join(s[0] for s in section)
    sec_start = section.pop()[1]
    if path in comments:
        for offset, comment in comments[path].items():
            pos = sec_start + offset
            if pos >= len(new_lines):
                indent = ''
            else:
                indent = new_lines[pos].count('\t')*'\t'
            
            if comment:
                comment = f'{indent}-- {comment}'
            else:
                comment = indent
            new_lines.insert(pos, comment)
    
    return '\n'.join(new_lines)

def split(path: str):
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
everything after the final slash.  Either part may be empty."""
    path_data = path.split('/')
    return '/'.join(path_data[:-1]), path_data[-1]

def section_to_walk(section: list) -> tuple:
    "Return folder and files from section"
    dirs: dict[str, list[str]] = {}
    for full_path in section:
        path, filename = split(full_path)
        if not path in dirs:
            dirs[path] = []
        dirs[path].append(filename)
    return tuple(dirs.items())

# lintcheck: too-many-locals (R0914): Too many local variables (18/15)
def update_comment_positions(original_pos: dict, new_data: dict, old_data: dict):
    "Update comment positions"
    # Get json of files
    old_json = json.dumps(old_data, indent='\t').splitlines()#.replace('\t', '').splitlines()
    new_json = json.dumps(new_data, indent='\t').splitlines()#.replace('\t', '').splitlines()
    
    new_comments: dict[str, dict[int, str]] = {}
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
            section_start = f'\t"{name}": ['
            obs = old_json.index(section_start)-1
            nbs = new_json.index(section_start)-1
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
    with open(filepath, 'r', encoding='utf-8') as file_point:
        fdata = file_point.read()
    return lang_to_json(fdata)

def write_lang_file(filepath: str, data: dict, comments: dict) -> None:
    "Write MineOS .lang file"
    with open(filepath, 'w', encoding='utf-8') as file_point:
        file_point.write(dict_to_lang(data, comments))

def partquotes(text: str, item: int, quotes: str='"') -> str:
    "Return item th part of text that is enclosed in quotes"
    return text.split(quotes)[2*item+1]

def dict_to_list(data: dict) -> tuple[list, list]:
    "Convert dictionary to two lists, one of keys, one of values."
    keys, values = [], []
    for key, value in data.items():
        if isinstance(key, int):
            key = f'{key}?'
        if isinstance(value, dict):
            enc_dict = [(f'{key}${key}$', value) for key, value in zip(*dict_to_list(value))]
            for dkey, dvalue in enc_dict:
                keys.append(dkey)
                values.append(dvalue)
        elif isinstance(value, list):
            enc_list = {f'{key}#{i}?#': v for i, v in enumerate(value)}
            for lkey, lvalue in zip(*dict_to_list(enc_list)):
                keys.append(lkey)
                values.append(lvalue)
        else:
            keys.append(key)
            values.append(value)
    return keys, values

def list_to_dict(keys: list, values: list) -> dict:
    "Convert split lists of compiled keys and values back into dictionary"
    # lintcheck: too-many-branches (R0912): Too many branches (19/12)
    def unwrap_keys(key_data: str, set_val: str, data: dict) -> None:
        pidx = 0
        while key_data:
            char_key_data = str(key_data)
            if ('$' in char_key_data or '#' in char_key_data):
                found = 0
                idx, char = 0, '"'
                for idx, char in enumerate(char_key_data):
                    if char in {'$', '#'}:
                        if found == (pidx*2):
                            break
                        found += 1
                parent = key_data[:idx]
                next_layer = partquotes(key_data, 0, char)
                
                parent_val: str | int = parent
##                next_layer_val: str | int = next_layer
                if parent.endswith('?'):
                    parent_val = int(parent[:-1])
##                if next_layer.endswith('?'):
##                    next_layer_val = int(next_layer[:-1])
                
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
                    data[int(key_data[:-1])] = set_val
                else:
                    data[key_data] = set_val
                key_data = ''
            pidx += 1
    data: dict = {}
    for key, value in zip(keys, values):
        unwrap_keys(key, value, data)
    return data

##k, v = dict_to_list({'cat': {3: '5', 7:'9', 4: [4, 3, 3]}, 'meep': [1, 2, [2, 3, 4]]})
##print((k, v))
##print(list_to_dict(k, v))

async def translate_file(data: dict, client, to_lang: str, src_lang: str='auto') -> dict:
    "Translate an entire file."
    keys, sentances = dict_to_list(data)
    results = await translate.translate_async(client, sentances,
                                              to_lang, src_lang)
    return list_to_dict(keys, results)

def translate_file_copy_paste(data: dict) -> dict:
    "Translate an entire file by creating text to paste into translator and reading the response"
    keys, sentances = dict_to_list(data)
    encoded = ' ###### '.join(sentances)
    print()
    print(encoded)
    print()
    raw_results = input('Paste result here: ')
    results = raw_results.split(' ###### ')
    return list_to_dict(keys, results)

def translate_files_copy_paste(file_dict_list: list) -> list[dict]:
    "Translate entire files by creating text to paste into translator and reading the response"
    all_enc = []
    all_keys = []
    for data in file_dict_list:
        keys, sentances = dict_to_list(data)
        encoded = ' ###### '.join(sentances)
        all_enc.append(encoded)
        all_keys.append(keys)
    print()
    print(' &&&&&& '.join(all_enc))
    print()
    raw_results = input('Paste result here: ')
    files = raw_results.split(' &&&&&& ')
    results = []
    for keys, enc_values in zip(all_keys, files):
        values = enc_values.split(' ###### ')
        results.append(list_to_dict(keys, values))
    return results

if __name__ == '__main__':
    print(f'{__title__} v{__version__}\nProgrammed by {__author__}.\n')
