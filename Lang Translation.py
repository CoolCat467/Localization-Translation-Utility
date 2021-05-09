#!/usr/bin/env python3
# Localization Translator Helper.
# -*- coding: utf-8 -*-

# Semi-compadable with Google Translate.
# When "translate" module present, completely compatable.

# Can use input from other files by changing the filename of
# the variable READ below.

READ = 'English.lang'
SRCLANG = 'en'

# For Lolcat, https://funtranslations.com/lolcat is known to work, "good" translator.

# Programmed by CoolCat467

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
__version__ = '2.0.0'
__ver_major__ = 2
__ver_minor__ = 0
__ver_patch__ = 0

def readData(filename):
    """Open filename and return data."""
    data = None
    with open(filename, mode='r') as readfile:
        data = readfile.read()
        readfile.close()
    return data

def writeData(filename, data):
    """Save <data> to <filename>."""
    with open(filename, mode='w', encoding='utf-8') as writefile:
        writefile.write(data)
        writefile.close()

def infIntGen(start=0, change=1):
    """Generate infinite intigers starting with <start> and incrementing by <change>."""
    n = int(start)
    c = int(change)
    while True:
        yield n
        n += c

def toJsonReadable(data):
    """Read the contents of file data <data> and fix variable names so json module can read it as json."""
    fixed = []
    lines = data.splitlines()
    for lidx in range(len(lines)):
        line = lines[lidx]
        cidx = line.find('=')
        cidx = cidx if cidx != -1 else 0
        # cidx is now pointing to equal sign in line after var name
        search = line[:cidx]
        # Skip invalid lines that end up saying nothing
        if not search:
            fixed.append(line)
            continue
        # Get variable title
        vartitle = search.split()[0]
        # Replace variable title with itself in double quotes
        line = line.replace(vartitle, '"'+vartitle+'"', 1)
        # Replace equal sign with colon
        line = line.replace('=', ':', 1)
        # Add the line to fixed lines
        fixed.append(line)
    if fixed[-2].endswith(','):
        fixed[-2] = fixed[-2][:-1]
    return '\n'.join(fixed)

def unJsonify(dictionary):
    """Dump dictionary to string with json module, then pretty much undo what's done in toJsonReadable."""
    # Specify how file format should be
    data = json.dumps(dictionary, ensure_ascii=False, separators=(',\n\t', ' = '))
    # Fix start and end
    data = '{\n\t'+data[1:-1]+'\n}'
    # Fix variable names
    fixed = []
    for line in data.splitlines():
        if ' = ' in line:
            namestop = line.index(' = ')
            line = '\t'+line[2:namestop-1]+line[namestop:]
        fixed.append(line)
    return '\n'.join(fixed)

def copy_paste_translation(data):
    """Convert dictionary into string with numbers and special markers, then take copy-paste output back and undo that so it's a dictionary again and return that."""
    # Make conversion dictionarys for between key and numbers and backwards
    # Create number to key dict with infinite number gen zipped with keys
    numToKey = {i:k for i, k in zip(infIntGen(), list(data.keys()))}
    # Make a reverse of that for keys to numbers
    keyToNum = {numToKey[k]:k for k in numToKey}
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

def automatic_translation(data):
    """Use the power of awesome google translate module cool guy made and translate stuff automatially for free!"""
    trans = {}
    language = input('Language code to translate to: (ex. "en", "zh-cn", "ru") : ')
    
    if not language in lang_globs.LANGUAGES:
        if language in lang_globs.LANGCODES:
            old = language
            language = lang_globs.LANGCODES[language]
            print(f'\nLanguage code "{old}" was not found, but it appears to corrospond with language code "{language}"!')
        else:
            print(f'\nLanguage code "{language}" not found in known language codes. Unexpected results may occour shorly.')
            input('Press Enter to Continue. ')
##    #pip3 install googletrans
##    itemCount = int(input('Number of lines to translate at once: '))
##    
##    ungroupedKeys = list(data.keys())
##    keyGroups = []
##    for i in range((len(ungroupedKeys) // itemCount) + 1):
##        topop = min(len(ungroupedKeys), itemCount)
##        if topop > 0:
##            keyGroups.append([ungroupedKeys.pop() for ii in range(topop)])
##    
##    translator = Translator()
##    
##    for keyGroup in keyGroups:
##        items = [data[key] for key in keyGroup]
##        translations = translator.translate(items, dest=language, src=SRCLANG)
##        for translation, key in zip(translations, keyGroup):
##            trans[key] = translation.text
##    if hasattr(translate, 'translate_sentances'):
    print('Translating sentances asyncronously...')
    keys = tuple(data.keys())
    values = translate.translate_sentances([data[key] for key in keys], language, SRCLANG)
    for key, value in zip(keys, values):
        trans[key] = value
##    else:
##        keys = tuple(data.keys())
##        lkeys = len(keys)
##        for kidx in range(lkeys):
##            key = keys[kidx]
##            trans[key] = translate.translate(data[key], language, SRCLANG)
##    ##        print(f'"{data[key]}" --> "{trans[key]}" ({kidx+1}/{lkeys})')
##            print(f'{kidx+1} / {lkeys} complete')
    
    print(f'\nDone translating to {lang_globs.LANGUAGES[language].title()}.')
    return trans

def automated_translation(to_language_codes, forMineOs=True):
    import asyncio
    if not CANAUTOTRANS:
        raise RuntimeError('Requires translate and lang_globs modules. Can be found in github repository.')
    to_language_codes = list(to_language_codes)
    
    if forMineOs:
        original = json.loads(toJsonReadable(readData(READ)))
    else:
        original = json.loads(readData(READ))
    
    def eval_code(code):
        if not code in lang_globs.LANGUAGES:
            if code in lang_globs.LANGCODES:
                old = language
                code = lang_globs.LANGCODES[code]
                print(f'\nLanguage code "{old}" was not found, but it appears to corrospond with language code "{code}"!')
            else:
                print(f'\nLanguage code "{code}" not found in known language codes.')
                if input('Would you like to replace its value? (y/N) ').lower() in ('y', 'yes'):
                    return eval_code(input('Replacement value: '))
                # In the event of no, leave it as is. Maybe language codes database is not complete.
        return code
    
    real_codes = []
    for language_code in to_language_codes:
        real_codes.append(eval_code(language_code))
    if SRCLANG in real_codes:
        del real_codes[real_codes.index(SRCLANG)]
    
    original_keys = tuple(original.keys())
    l_orig_keys = len(original_keys)
    original_sentances = [original[key] for key in original_keys]
    
    async def save_language(langcode, dictionary):
        filename = lang_globs.LANGUAGES[langcode].title()+'.lang'
        if forMineOs:
            writeData(filename, unJsonify(dictionary))
        else:
            writeData(filename, json.dumps(dictionary))
        print(f'Saved {langcode} to {filename}.')
    
    async def translate_to_language(loop, langcode):
        print(f'Translating {langcode}...')
        trans_sent = await translate.translate_async(loop, original_sentances,
                                                     langcode, SRCLANG)
        trans_dict = {original_keys[i]:trans_sent[i] for i in range(l_orig_keys)}
##        return trans_dict
        print(f'Translatation to {langcode} complete.')
        await save_language(langcode, trans_dict)
    
    async def translate_all_languages(loop):
        for lc in real_codes:
            await translate_to_language(loop, lc)
##        coros = [translate_to_language(loop, lc) for lc in real_codes]
##        await asyncio.gather(*coros)
    
    # Get asyncronous event loop
    event_loop = asyncio.get_event_loop()
    print(f'Beginning translation to {len(real_codes)} languages...')
    try:
        event_loop.run_until_complete(translate_all_languages(event_loop))
    finally:
        # Close the event loop no matter what
        event_loop.close()
    del asyncio
##    translate_all_languages()
    print(f'\nTranslation of {len(real_codes)} languages complete!')

def run():
    print('\nDo not run in windows powershell, or really any shell for that\nmatter. Program is prone to crash and tells you how to fix before crash.\nIdle is a much better idea.\n')
    
    notMineos = False
    if input('Is input lang file for MineOS? (Y/n) ').lower() in ('n', 'no'):
        data = json.loads(readData(READ))
        notMineos = True
    else:
        data = json.loads(toJsonReadable(readData(READ)))
    
    if CANAUTOTRANS and input(f'Would you like to auto-translate the {READ.split(".")[0]} to specified with google translate? (y/N) : ').lower() in ('y', 'yes'):
        trans = automatic_translation(data)
    else:
        trans = copy_paste_translation(data)
    
    # Get language name from user
    lang = input('\nLanguage save name: ')
    # Save file is language string + '.lang'
    filename = lang+'.lang'
    
    if notMineos:
        writeData(filename, json.dumps(trans))
    else:
        writeData(filename, unJsonify(trans))
    
##    automated_translation(tuple(lang_globs.LANGUAGES.keys()))

if __name__ == '__main__':
    print('%s v%s\nProgrammed by %s.' % (__title__, __version__, __author__))
    run()
