#!/usr/bin/env python3
# Localization Translator Helper.
# -*- coding: utf-8 -*-

# Semi-compadable with Google Translate using copy-paste nonsense.
# When "translate" module present, completely compatable.

# For Lolcat, https://funtranslations.com/lolcat is known to work, "good" translator.

# Programmed by CoolCat467

import os
import asyncio
import json

CANAUTOTRANS = False
try:
    import translate
    import lang_globs
except ImportError:
    pass
else:
    CANAUTOTRANS = True

__title__ = 'Localization Translator Helper'
__author__ = 'CoolCat467'
__version__ = '2.1.0'
__ver_major__ = 2
__ver_minor__ = 1
__ver_patch__ = 0

def readData(filename):
    """Open filename and return data."""
    with open(filename, mode='r') as readfile:
        data = readfile.read()
        readfile.close()
    return data

def writeData(filename, data):
    """Save <data> to <filename>."""
    with open(filename, mode='w', encoding='utf-8') as writefile:
        writefile.write(data)
        writefile.close()

def toJsonReadable(data):
    """Read the contents of file data <data> and fix variable names so json module can read it as json."""
    fixed = []
    # Lines is all the lines, seperated by splitlines,
    # while making tiny chuncks seperate lines so vartitle fix happens,
    # and also avoiding comment lines because that breaks everything.
    lines = [line for line in data.replace(', ', ',\n').splitlines() if not '--' in line]
    # Chunks is initialized with giant main chunk or IndexError happens from pop.
    chuncks = [[0, '{}']]
    for lidx in range(len(lines)):
        line = lines[lidx]
        cidx = line.find('=')
        cidx = cidx if cidx != -1 else 0
        # cidx is now pointing to equal sign in line after var name
        search = line[:cidx]
        # If this line is the end of a chunk
        if '}' in line:
            # Get the previous line
            lline = fixed[lidx-1]
            # If it ended with a trailing comma,
            if lline.endswith(','):
                # Remove the trailing comma and don't break things
                fixed[lidx-1] = lline[:-1]
            # Now, pop the chunk we were reading's start and type.
            start, totype = chuncks.pop()
            # If we need to modify it (change to list),
            if totype == '[]':
                # The start of the chunk should have its curly bracket changed
                # into a square bracket
                fixed[start] = fixed[start].replace('{', '[', 1)
                # Replace this line (chunk end) curly bracket with square bracket
                line = line.replace('}', ']', 1)
        # Skip invalid lines that end up saying nothing
        if not search:
            # Add this line to the fixed lines and skip vartitle fixing
            fixed.append(line)
            continue
        # If this line is the start of a chunk,
        if '{' in line:
            # Everything is a dictionary by default
            cnktype = '{}'
            # If the next line has another chunk start,
            if '{' in lines[lidx+1]:
                # Chunk type is list
                cnktype = '[]'
            # If next line isn't another chunk but it's not a dictionary,
            elif not '=' in lines[lidx+1]:
                # it's also a list.
                cnktype = '[]'
            # Add new chunk to chunks que
            chuncks.append([lidx, cnktype])
        # Get variable title
        varsplt = search.split()
        # Don't select chunk starts
        vartitle = varsplt[0 if not '{' in varsplt else 1]
        # Replace variable title with itself in double quotes
        line = line.replace(vartitle, '"'+vartitle+'"', 1)
        # Replace equal sign with colon
        line = line.replace('=', ':', 1)
        # Add the line to fixed lines
        fixed.append(line)
    # Finally, return fixed as linebroken string, fixing comma problems while we do that.
    return '\n'.join(fixed).replace('\n"', ', "').replace(',,', ',')

def partQuotes(text, which, quotes="'"):
    """Return part which of text within quotes."""
    return text.split(quotes)[which*2+1]

def unJsonify(dictionary, indent='\t', modifyNames=True):
    """Dump dictionary to string with json module, then pretty much undo what's done in toJsonReadable if modifyNames is True."""
    # Specify how file format should be
    separators = (',', ' = ' if modifyNames else ': ')
    data = json.dumps(dictionary, ensure_ascii=False,
                      separators=separators,
                      indent=indent)
    if modifyNames:
        # Change variable names to not be in quotes.
        fixed = []
        for line in data.splitlines():
            if ' = ' in line:
                namestop = line.index(' = ')
                line = indent+partQuotes(line, 0, '"')+line[namestop:]
            fixed.append(line)
        return '\n'.join(fixed)
    return data

def copy_paste_translation(data):
    """Convert dictionary into string with numbers and special markers, then take copy-paste output back and undo that so it's a dictionary again and return that."""
    # Make conversion dictionarys for between key and numbers and backwards
    # Create number to key dict with infinite number gen zipped with keys
    keys = list(data.keys())
    numToKey = {i:keys[i] for i in range(len(keys))}
    # Make a reverse of that for keys to numbers
    keyToNum = dict(map(reversed, numToKey.items()))
    # Generate data to paste in translator
    toPaste = ''
    # For all the keys in our data,
    for key in data:
        # Get the number that corelates with that key
        num = keyToNum[key]
        # Add '#<key number>*<value>' to toPaste data
        toPaste += ('#%i*' % num) + data[key].replace('\n', '_n_')
    # Print for user and get translated back
    print('Copy-paste the following into some sort of translator (text within single quotes):')
    print("'"+toPaste+"'")
    # Get translated back from user
    copied = input('Enter translated result: ')
    # If it's google translate, we need to fix data
    isbad = not input('Is translator nice? (output is not split by spaces)(y/N) : ').lower() in ('y', 'yes')
    # If used bad (like google translate and it added spaces), fix it
    if isbad:
        # Fix weirdness google translate adds to our fine data
        hashfx = copied.replace(' # ', '#')
        hashfx2 = hashfx.replace('# ', '#')
        hashfx3 = hashfx2.replace(' #', '#')
        starfx = hashfx3.replace(' * ', '*')
        hashfx4 = starfx.replace('#\u200b\u200b', '#')
        copied = hashfx4        
        print('In some cases, may be so evil user has to help. Warning.')
        print('Printing lines so you can fix parsing problems.')
    # Decode translated data back into usable dictionary
    trans = {}
    # Get return characters back from data we changed earlier
    # and then get lines from the pound characters, and ignore the
    # first one which ends up being ''.
    lines = copied.replace('_n_', '\n').split('#')[1:]
    # For each line in output,
    for line in lines:
        # Seperate key number from data by splitting by '*' characters
        split = line.split('*')
        # If split data is empty, skip this line.
        if split == ['']:
            continue
        # If we are using google translate, print the line in case of errors
        if isbad:
            print(line)
        # If there is invalid split data, tell user and prepare for crash :(
        if len(split) != 2:
            print('An error is about to occor very likely.')
            print('Line data: "%s"' % line)
            print('Seperated Data: %r' % split)
        # Get number and value from split data
        num, value = split
        # Add data to translated dictionary and convert key number back to real key.
        trans[numToKey[int(num)]] = value
    return trans

def automatic_translation(data, from_lang='auto'):
    """Use the power of awesome google translate module cool guy made and translate stuff automatially for free!"""
    language = input('Language code to translate to: (ex. "en", "zh-cn", "ru") : ')
    
    if not language in lang_globs.LANGUAGES:
        if language in lang_globs.LANGCODES:
            old = language
            language = lang_globs.LANGCODES[language]
            print(f'\nLanguage code "{old}" was not found, but it appears to corrospond with language code "{language}"!')
        else:
            print(f'\nLanguage code "{language}" not found in known language codes. Unexpected results may occour shorly.')
            input('Press Enter to Continue. ')
    
    print('Translating sentances asyncronously...')
    keys = tuple(data.keys())
    values = translate.translate_sentances([data[key] for key in keys], language, from_lang)
    trans = dict(zip(keys, values))
    
    print(f'\nDone translating to {lang_globs.LANGUAGES[language].title()}.')
    return trans

def automated_translation(to_language_codes, from_filename, from_lang='auto', saveFiles=True, saveFilename='{}.lang', fastest=False, forMineOs=True, doPrint=True):
    """Automated translation of a language file. Returns massive dictionary of translated, with codes as keys. See help() for this function for more information.
    
    Automated translation of a language file from language from_lang
    to all languages specified by to_language_codes.
    
    If saveFile is True, save the files in the folder "Translated" in the
    current directory. Will create folder if it does not exist.
    
    saveFilename should be a formatable string with an extention, ex "{}.txt" or
    "{}.json" or "{}.lang", where {} gets subsituted by the language name.
    Again, all of these files will appear in the program's current running
    directory in a directory labled "Translated".
    
    If fastest is True, run all translations asyncronously,
    which will likely cause a aiohttp error for too many open files
    because of the way things get translated. It can work for
    smaller jobs though, so that's why it exists.
    
    If forMineOs is True, modify the from_filename read data so the
    json module can parse it properly and we can actually do things.
    Set it to false if you are reading plain json files.
    """
    if not CANAUTOTRANS:
        raise RuntimeError('Requires translate and lang_globs modules. Can be found in github repository.')
    if doPrint:
        pront = lambda x: print(x)
    else:
        pront = lambda x: None
    
    to_language_codes = list(to_language_codes)
    
    fileData = readData(from_filename)
    if forMineOs:
        fileData = toJsonReadable(fileData)
    original = json.loads(fileData)
    
    def eval_code(code):
        """Evaluate language code for validity."""
        if not code in lang_globs.LANGUAGES:
            if code in lang_globs.LANGCODES:
                old = language
                code = lang_globs.LANGCODES[code]
                pront(f'\nLanguage code "{old}" was not found, but it appears to corrospond with language code "{code}"!')
            elif doPrint:
                print(f'\nLanguage code "{code}" not found in known language codes.')
                if input('Would you like to replace its value? (y/N) ').lower() in ('y', 'yes'):
                    return eval_code(input('Replacement value: '))
                # In the event of no, leave it as is. Maybe language codes
                # database is not complete.
        return code
    
    real_codes = []
    for language_code in to_language_codes:
        real_codes.append(eval_code(language_code))
    if from_lang in real_codes:
        del real_codes[real_codes.index(from_lang)]
    
    original_keys = tuple(original.keys())
    l_orig_keys = len(original_keys)
    original_sentances = [original[key] for key in original_keys]
    
    async def save_language(langcode, dictionary):
        """Save a language data from dictionary to a file, filename based on langcode and saveFilename."""
        lang_name = lang_globs.LANGUAGES[langcode].title()
        filename = saveFilename.format(lang_name)
        if not os.path.exists('Translated/'):
            os.mkdir('Translated')
        filename = 'Translated/'+filename
        if forMineOs:
            writeData(filename, unJsonify(dictionary))
        else:
            writeData(filename, json.dumps(dictionary, ensure_ascii=False))
        print(f'Saved {langcode} to {filename}.')
    
    async def translate_to_language(loop, langcode, save=True):
        """Translate the original file to language specified by langcode, and save is save is True."""
        pront(f'Translating {langcode}...')
        trans_sent = await translate.translate_async(loop, original_sentances,
                                                     langcode, from_lang)
        trans_dict = {original_keys[i]:trans_sent[i] for i in range(l_orig_keys)}
        pront(f'Translatation to {langcode} complete.')
        if save:
            await save_language(langcode, trans_dict)
        return langcode, trans_dict
    
    async def translate_all_languages(loop, fastest=False, save=True):
        """Translate original file to all languages defined by to_lang_codes. Save files if save is True."""
        if fastest:
            coros = [translate_to_language(loop, lc, save) for lc in real_codes]
            results = await asyncio.gather(*coros)
        else:
            results = []
            for lc in real_codes:
                results.append(await translate_to_language(loop, lc, save))
        results = {langcode:transdict for langcode, transdict in results}
        return results
    
    # Get asyncronous event loop
    event_loop = asyncio.get_event_loop()
    pront(f'Beginning translation to {len(real_codes)} languages...')
    results = event_loop.run_until_complete(translate_all_languages(event_loop))
    pront(f'\nTranslation of {len(real_codes)} languages complete!')
    return results

def terminate():
    """Gracefully quit the program after user presses return key."""
    input('\nPress RETURN to continue. ')
    os.sys.exit()
    exit()
    os.abort()

def run():
    print('\nDo not run in windows powershell, or really any shell for that\nmatter. Program is prone to crash and tells you how to fix before crash.\nIdle is a much better idea.\n')
    
    loadFilename = input('Filename to load: ')
    
    try:
        fileext = '.'+loadFilename.split('.')[-1]
        fileData = readData(loadFilename)
    except Exception as ex:
        print(f'\nA {type(ex).__name__} Error Has Occored: {", ".join(map(str, ex.args))}')
        print('Error: Invalid filename.')
        return terminate()
    
    mineos = input('Is input lang file for MineOS? (y/N) ').lower() in ('y', 'yes')
    
    if mineos:
        fileData = toJsonReadable(fileData)
    try:
        data = json.loads(fileData)
    except Exception as ex:
        print(f'\nA {type(ex).__name__} Error Has Occored: {", ".join(map(str, ex.args))}')
        print('Error: Invalid file data.')
        return terminate()
    
    try:
        if CANAUTOTRANS and not input(f'Would you like to auto-translate with google translate? (Y/n) : ').lower() in ('n', 'no'):
            trans = automatic_translation(data)
        else:
            trans = copy_paste_translation(data)
    except Exception as ex:
        print(f'\nA {type(ex).__name__} Error Has Occored: {", ".join(map(str, ex.args))}')
        print('Error: Invalid translation response.')
        return terminate()
    
    try:
        indent = fileData[fileData.index('\n')+1:fileData.index('"')]
    except Exception:
        indent = '\t'
    print(f'\nAssummed file indentation: "{indent}"')
    if input('Change to a different value? (y/N) : ').lower() in ('y', 'yes'):
        indent = input('New indent: ').replace('\\t', '\t').replace('\\n', '\n')
    
    # Get language name from user
    lang = input('\nNew language filename (no extention): ')
    # Save file is language string + the extention used in the loaded file.
    saveFilename = lang+fileext
    
    try:
        writeData(saveFilename, unJsonify(trans, indent, mineos))
    except Exception as ex:
        print(f'\nA {type(ex).__name__} Error Has Occored: {", ".join(map(str, ex.args))}')
        print('Error: Could not save file.')
        return terminate()
    else:
        print(f'\nSuccessfully saved as "{saveFilename}" in "{os.getcwd()}".')
    return terminate()

if __name__ == '__main__':
    print('%s v%s\nProgrammed by %s.' % (__title__, __version__, __author__))
    run()
####    automated_translation(tuple(lang_globs.LANGUAGES.keys()))
##    langs = ['af', 'sq', 'am', 'hy', 'az', 'eu', 'be', 'bs', 'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'eo', 'et', 'tl', 'fy', 'gl', 'ka', 'el', 'gu', 'ht', 'ha', 'haw', 'he', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'jw', 'kn', 'kk', 'km', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'or', 'ps', 'fa', 'pa', 'ro', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sl', 'so', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu']
##    automated_translation(langs)
