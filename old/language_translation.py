#!/usr/bin/env python3
# Localization Translator Helper.
# -*- coding: utf-8 -*-

"Language translation assistant tool"

# Semi-compadable with Google Translate using copy-paste nonsense.
# When "translate" module present, completely compatible.

# For Lolcat, https://funtranslations.com/lolcat is known to work, "good" translator.

# Programmed by CoolCat467

import asyncio
import json
import os

CAN_AUTO_TRANS = False
try:
    import lang_globs

    import translate
except ImportError:
    pass
else:
    CAN_AUTO_TRANS = True

__title__ = "Localization Translator Helper"
__author__ = "CoolCat467"
__version__ = "2.2.0"
__ver_major__ = 2
__ver_minor__ = 2
__ver_patch__ = 0


def read_file(filename):
    "Open filename and return data."
    with open(filename, encoding="utf-8") as readfile:
        data = readfile.read()
        readfile.close()
    return data


def write_file(filename, data):
    "Save <data> to <filename>."
    with open(filename, mode="w", encoding="utf-8") as writefile:
        writefile.write(data)
        writefile.close()


def fix_json(data):
    "Read <data> and fix variable names it's readable as json."
    fixed = []
    # Lines is all the lines, separated by splitlines,
    # while making tiny chunks separate lines so vartitle fix happens,
    # and also avoiding comment lines because that breaks everything.
    lines = [
        line
        for line in data.replace(", ", ",\n").splitlines()
        if "--" not in line
    ]
    # Chunks is initialized with giant main chunk or IndexError happens from pop.
    chunks = [[0, "{}"]]
    # lintcheck: consider-using-enumerate (C0200): Consider using enumerate instead of iterating with range and len
    for lidx in range(len(lines)):
        line = lines[lidx]
        cidx = line.find("=")
        cidx = cidx if cidx != -1 else 0
        # cidx is now pointing to equal sign in line after var name
        search = line[:cidx]
        # If this line is the end of a chunk
        if "}" in line:
            # Get the previous line
            lline = fixed[lidx - 1]
            # If it ended with a trailing comma,
            if lline.endswith(","):
                # Remove the trailing comma and don't break things
                fixed[lidx - 1] = lline[:-1]
            # Now, pop the chunk we were reading's start and type.
            start, totype = chunks.pop()
            # If we need to modify it (change to list),
            if totype == "[]":
                # The start of the chunk should have its curly bracket changed
                # into a square bracket
                fixed[start] = fixed[start].replace("{", "[", 1)
                # Replace this line (chunk end) curly bracket with square bracket
                line = line.replace("}", "]", 1)
        # Skip invalid lines that end up saying nothing
        if not search:
            # Add this line to the fixed lines and skip vartitle fixing
            fixed.append(line)
            continue
        # If this line is the start of a chunk,
        if "{" in line:
            # Everything is a dictionary by default
            cnktype = "{}"
            # If the next line has another chunk start,
            if "{" in lines[lidx + 1]:
                # Chunk type is list
                cnktype = "[]"
            # If next line isn't another chunk but it's not a dictionary,
            elif "=" not in lines[lidx + 1]:
                # it's also a list.
                cnktype = "[]"
            # Add new chunk to chunks que
            chunks.append([lidx, cnktype])
        # Get variable title
        varsplt = search.split()
        # Don't select chunk starts
        vartitle = varsplt[0 if "{" not in varsplt else 1]
        # Replace variable title with itself in double quotes
        line = line.replace(vartitle, '"' + vartitle + '"', 1)
        # Replace equal sign with colon
        line = line.replace("=", ":", 1)
        # Add the line to fixed lines
        fixed.append(line)
    # Finally, return fixed as linebroken string, fixing comma problems while we do that.
    return "\n".join(fixed).replace('\n"', ', "').replace(",,", ",")


def part_quotes(text, which, quotes="'"):
    "Return part which of text within quotes."
    return text.split(quotes)[which * 2 + 1]


# lintcheck: invalid-name (C0103): Argument name "modifyNames" doesn't conform to snake_case naming style
def break_json(dictionary, indent="\t", modifyNames=True):
    # lintcheck: line-too-long (C0301): Line too long (119/100)
    "Dump dictionary to string with json module, then pretty much undo what's done in fix_json if modifyNames is True."
    # Specify how file format should be
    separators = (",", " = " if modifyNames else ": ")
    data = json.dumps(
        dictionary, ensure_ascii=False, separators=separators, indent=indent
    )
    if modifyNames:
        # Change variable names to not be in quotes.
        fixed = []
        for line in data.splitlines():
            if " = " in line:
                namestop = line.index(" = ")
                line = indent + part_quotes(line, 0, '"') + line[namestop:]
            fixed.append(line)
        return "\n".join(fixed)
    return data


def copy_paste_translation(data):
    # lintcheck: line-too-long (C0301): Line too long (161/100)
    "Convert dictionary into string with numbers and special markers, then take copy-paste output back and undo that so it's a dictionary again and return that."
    # Make conversion dictionaries for between key and numbers and backwards
    # Create number to key dict with infinite number gen zipped with keys
    keys = list(data.keys())
    # lintcheck: unnecessary-comprehension (R1721): Unnecessary use of a comprehension, use dict(enumerate(keys)) instead.
    key_dict = {idx: val for idx, val in enumerate(keys)}
    # Make a reverse of that for keys to numbers
    rev_key_dict = dict(map(reversed, key_dict.items()))
    # Generate data to paste in translator
    to_paste = ""
    # For all the keys in our data,
    for key in data:
        # Get the number that correlates with that key
        num = rev_key_dict[key]
        # Add '#<key number>*<value>' to to_paste data
        # lintcheck: consider-using-f-string (C0209): Formatting a regular string which could be a f-string
        to_paste += ("#%i*" % num) + data[key].replace("\n", "_n_")
    # Print for user and get translated back
    print(
        "Copy-paste the following into some sort of translator (text within single quotes):"
    )
    print("'" + to_paste + "'")
    # Get translated back from user
    copied = input("Enter translated result: ")
    # If it's google translate, we need to fix data
    # lintcheck: line-too-long (C0301): Line too long (109/100)
    is_bad = input(
        "Is translator nice? (output is not split by spaces)(y/N) : "
    ).lower() not in ("y", "yes")
    # If used bad (like google translate and it added spaces), fix it
    if is_bad:
        # Fix weirdness google translate adds to our fine data
        fix = copied.replace(" # ", "#")
        fix = fix.replace("# ", "#")
        fix = fix.replace(" #", "#")
        fix = fix.replace(" * ", "*")
        fix = fix.replace("#\u200b\u200b", "#")
        copied = fix
        print("In some cases, may be so evil user has to help. Warning.")
        print("Printing lines so you can fix parsing problems.")
    # Decode translated data back into usable dictionary
    trans = {}
    # Get return characters back from data we changed earlier
    # and then get lines from the pound characters, and ignore the
    # first one which ends up being ''.
    lines = copied.replace("_n_", "\n").split("#")[1:]
    # For each line in output,
    for line in lines:
        # Separate key number from data by splitting by '*' characters
        split = line.split("*")
        # If split data is empty, skip this line.
        if split == [""]:
            continue
        # If we are using google translate, print the line in case of errors
        if is_bad:
            print(line)
        # If there is invalid split data, tell user and prepare for crash :(
        if len(split) != 2:
            print("An error is about to occor very likely.")
            print(f'Line data: "{line}"')
            print(f"Separated Data: {split}")
        # Get number and value from split data
        num, value = split
        # Add data to translated dictionary and convert key number back to real key.
        trans[key_dict[int(num)]] = value
    return trans


def automatic_translation(data, from_lang="auto"):
    # lintcheck: line-too-long (C0301): Line too long (111/100)
    "Use the power of awesome google translate module cool guy made and translate stuff automatically for free!"
    language = input(
        'Language code to translate to: (ex. "en", "zh-cn", "ru") : '
    )

    if language not in lang_globs.LANGUAGES:
        if language in lang_globs.LANGCODES:
            old = language
            language = lang_globs.LANGCODES[language]
            # lintcheck: line-too-long (C0301): Line too long (122/100)
            print(
                f'\nLanguage code "{old}" was not found, but it appears to correspond with language code "{language}"!'
            )
        else:
            # lintcheck: line-too-long (C0301): Line too long (123/100)
            print(
                f'\nLanguage code "{language}" not found in known language codes. Unexpected results may occur shortly.'
            )
            input("Press Enter to Continue. ")

    print("Translating sentences asynchronously...")
    keys = tuple(data.keys())
    values = translate.translate_sentances(
        [data[key] for key in keys], language, from_lang
    )
    trans = dict(zip(keys, values))

    print(f"\nDone translating to {lang_globs.LANGUAGES[language].title()}.")
    return trans


# lintcheck: line-too-long (C0301): Line too long (164/100)
def automated_translation(
    to_language_codes,
    from_filename,
    from_lang="auto",
    saveFiles=True,
    saveFilename="{}.lang",
    fastest=False,
    for_mineos=True,
    doPrint=True,
):
    # lintcheck: line-too-long (C0301): Line too long (161/100)
    """Automated translation of a language file. Returns massive dictionary of translated, with codes as keys. See help() for this function for more information.

    Automated translation of a language file from language from_lang
    to all languages specified by to_language_codes.

    If saveFile is True, save the files in the folder "Translated" in the
    current directory. Will create folder if it does not exist.

    saveFilename should be a formatable string with an extension, ex "{}.txt" or
    "{}.json" or "{}.lang", where {} gets substituted by the language name.
    Again, all of these files will appear in the program's current running
    directory in a directory labled "Translated".

    If fastest is True, run all translations asynchronously,
    which will likely cause a aiohttp error for too many open files
    because of the way things get translated. It can work for
    smaller jobs though, so that's why it exists.

    If for_mineos is True, modify the from_filename read data so the
    json module can parse it properly and we can actually do things.
    Set it to false if you are reading plain json files.
    """
    if not CAN_AUTO_TRANS:
        # lintcheck: line-too-long (C0301): Line too long (107/100)
        raise RuntimeError(
            "Requires translate and lang_globs modules. Can be found in github repository."
        )
    if doPrint:
        # lintcheck: unnecessary-lambda (W0108): Lambda may not be necessary
        pront = lambda x: print(x)
    else:
        pront = lambda x: None

    to_language_codes = list(to_language_codes)

    file_data = read_file(from_filename)
    if for_mineos:
        file_data = fix_json(file_data)
    original = json.loads(file_data)

    try:
        indent = file_data[file_data.index("\n") + 1 : file_data.index('"')]
    # lintcheck: broad-except (W0703): Catching too general exception Exception
    except Exception:
        indent = "\t"
    print(f'\nAssummed file indentation: "{indent}"')
    if input("Change to a different value? (y/N) : ").lower() in ("y", "yes"):
        indent = (
            input("New indent: ").replace("\\t", "\t").replace("\\n", "\n")
        )

    def eval_code(code):
        "Evaluate language code for validity."
        if code not in lang_globs.LANGUAGES:
            if code in lang_globs.LANGCODES:
                old = code
                code = lang_globs.LANGCODES[code]
                # lintcheck: line-too-long (C0301): Line too long (122/100)
                pront(
                    f'\nLanguage code "{old}" was not found, but it appears to correspond with language code "{code}"!'
                )
            elif doPrint:
                print(
                    f'\nLanguage code "{code}" not found in known language codes.'
                )
                if input(
                    "Would you like to replace its value? (y/N) "
                ).lower() in (
                    "y",
                    "yes",
                ):
                    return eval_code(input("Replacement value: "))
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
        # lintcheck: line-too-long (C0301): Line too long (102/100)
        "Save a language data from dictionary to a file, filename based on langcode and saveFilename."
        ##        lang_name = lang_globs.LANGUAGES[langcode].title()
        ##        filename = saveFilename.format(lang_name)
        filename = saveFilename.format(langcode)
        if not os.path.exists("Translated/"):
            os.mkdir("Translated")
        filename = "Translated/" + filename
        write_file(filename, break_json(dictionary, indent, for_mineos))
        print(f"Saved {langcode} to {filename}.")

    async def translate_to_language(loop, langcode, save=True):
        "Translate the original file to language specified by langcode, and save is save is True."
        pront(f"Translating {langcode}...")
        trans_sent = await translate.translate_async(
            loop, original_sentances, langcode, from_lang
        )
        trans_dict = {
            original_keys[i]: trans_sent[i] for i in range(l_orig_keys)
        }
        pront(f"Translatation to {langcode} complete.")
        if save:
            await save_language(langcode, trans_dict)
        return langcode, trans_dict

    async def translate_all_languages(loop, fastest=False, save=True):
        # lintcheck: line-too-long (C0301): Line too long (104/100)
        "Translate original file to all languages defined by to_lang_codes. Save files if save is True."
        if fastest:
            coros = [
                translate_to_language(loop, lc, save) for lc in real_codes
            ]
            results = await asyncio.gather(*coros)
        else:
            results = []
            # lintcheck: invalid-name (C0103): Variable name "lc" doesn't conform to snake_case naming style
            for lc in real_codes:
                results.append(await translate_to_language(loop, lc, save))
        return dict(results)

    # Get asynchronous event loop
    event_loop = asyncio.new_event_loop()
    pront(f"Beginning translation to {len(real_codes)} languages...")
    results = event_loop.run_until_complete(
        translate_all_languages(event_loop)
    )
    event_loop.close()
    pront(f"\nTranslation of {len(real_codes)} languages complete!")
    return results


def terminate():
    "Gracefully quit the program after user presses return key."
    input("\nPress RETURN to continue. ")
    os.sys.exit()
    # lintcheck: consider-using-sys-exit (R1722): Consider using sys.exit()
    exit()
    os.abort()


# lintcheck: missing-function-docstring (C0116): Missing function or method docstring
def run():
    # lintcheck: line-too-long (C0301): Line too long (182/100)
    print(
        "\nDo not run in windows powershell, or really any shell for that\nmatter. Program is prone to crash and tells you how to fix before crash.\nIdle is a much better idea.\n"
    )

    load_filename = input("Filename to load: ")

    try:
        file_ext = "." + load_filename.split(".")[-1]
        file_data = read_file(load_filename)
    # lintcheck: broad-except (W0703): Catching too general exception Exception
    except Exception as ex:
        print(
            f'\nA {type(ex).__name__} Error Has Occored: {", ".join(map(str, ex.args))}'
        )
        print("Error: Invalid filename.")
        return terminate()

    mineos = input("Is input lang file for MineOS? (y/N) ").lower() in (
        "y",
        "yes",
    )

    if mineos:
        file_data = fix_json(file_data)
    try:
        data = json.loads(file_data)
    # lintcheck: broad-except (W0703): Catching too general exception Exception
    except Exception as ex:
        print(
            f'\nA {type(ex).__name__} Error Has Occored: {", ".join(map(str, ex.args))}'
        )
        print("Error: Invalid file data.")
        return terminate()

    try:
        # lintcheck: line-too-long (C0301): Line too long (132/100)
        if CAN_AUTO_TRANS and input(
            "Would you like to auto-translate with google translate? (Y/n) : "
        ).lower() not in ("n", "no"):
            trans = automatic_translation(data)
        else:
            trans = copy_paste_translation(data)
    # lintcheck: broad-except (W0703): Catching too general exception Exception
    except Exception as ex:
        print(
            f'\nA {type(ex).__name__} Error Has Occored: {", ".join(map(str, ex.args))}'
        )
        print("Error: Invalid translation response.")
        return terminate()

    try:
        indent = file_data[file_data.index("\n") + 1 : file_data.index('"')]
    # lintcheck: broad-except (W0703): Catching too general exception Exception
    except Exception:
        indent = "\t"
    print(f'\nAssummed file indentation: "{indent}"')
    if input("Change to a different value? (y/N) : ").lower() in ("y", "yes"):
        indent = (
            input("New indent: ").replace("\\t", "\t").replace("\\n", "\n")
        )

    # Get language name from user
    lang = input("\nNew language filename (no extension): ")
    # Save file is language string + the extension used in the loaded file.
    # lintcheck: invalid-name (C0103): Variable name "saveFilename" doesn't conform to snake_case naming style
    saveFilename = lang + file_ext

    try:
        write_file(saveFilename, break_json(trans, indent, mineos))
    # lintcheck: broad-except (W0703): Catching too general exception Exception
    except Exception as ex:
        print(
            f'\nA {type(ex).__name__} Error Has Occored: {", ".join(map(str, ex.args))}'
        )
        print("Error: Could not save file.")
        return terminate()
    else:
        print(f'\nSuccessfully saved as "{saveFilename}" in "{os.getcwd()}".')
    return terminate()


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.")
    run()
####    automated_translation(tuple(lang_globs.LANGUAGES.keys()))
# lintcheck: line-too-long (C0301): Line too long (551/100)
##    langs = ['af', 'sq', 'am', 'hy', 'az', 'eu', 'be', 'bs', 'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'eo', 'et', 'tl', 'fy', 'gl', 'ka', 'el', 'gu', 'ht', 'ha', 'haw', 'he', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'jw', 'kn', 'kk', 'km', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'or', 'ps', 'fa', 'pa', 'ro', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sl', 'so', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu']
##    automated_translation(langs)
