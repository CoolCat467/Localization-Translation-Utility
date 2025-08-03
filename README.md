# Localization-Translation-Utility
Script for simplifying the process of translating Language (.lang) files

<!-- BADGIE TIME -->

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/CoolCat467/Localization-Translation-Utility/main.svg)](https://results.pre-commit.ci/latest/github/CoolCat467/Localization-Translation-Utility/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

<!-- END BADGIE TIME -->

Supports MineOS lang files, which is the main purpose of this project's existence

## Installation
```console
pip install git+https://github.com/CoolCat467/Localization-Translation-Utility.git
```

## Usage
WARNING: Creating hundreds of new files takes up a lot of space on your computer!
This program may require more than 3.5 MB to store the new localizations alone!

```console
> mineos_translate
usage: mineos_translate [-h] [-V] [-u | -b | -l] [-f FILENAME] [-k KEY]

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -u, --unhandled       Translate unhandled languages
  -b, --broken          Translate broken values
  -l, --lolcat          Translate to lolcat

  -f FILENAME, --filename FILENAME
  -k KEY, --key KEY
```

When run with any valid option, program will download `Installer/Files.cfg` from
MineOS repo, save downloaded files to `mineos_cache` folder it creates in the current working directory,
and save translated results in `mineos_upload` folder it creates in the current working directory.

### Unhandled mode
For every language code in `languages.py` (from https://github.com/ssut/py-googletrans/blob/master/googletrans/constants.py)
it will use google translate with different user agents from `agents.py` (from
https://github.com/Animenosekai/useragents/blob/main/pyuseragents/data/list.py) to translate
the English localization to that language and save the new file in the `mineos_upload` folder
it creates.

### Broken mode
For all existing localization files, if the value is identical to the value the English localization uses,
translate the value from the English localization to that language using google translate and save new file
in the `mineos_upload` folder it creates.

### Lolcat mode
For all localization directories, if an English localization exists and there is not a Lolcat translation,
use web scraper to talk to `funtranslations.com/lolcat` and translate the English localization to Lolcat
and save new file in the `mineos_upload` folder the program creates.

### Translating a new key for a specific program
Pass the filename and key parameters and the program will get the English localization of the program specified
by the folder given as the `filename` input and will use google translate to translate the localization
key specified by the `key` parameter. New files saved in the `mineos_upload` folder the program creates.


General code layout:

`cli.py` is the command line interface handler.

`mineos_auto_trans.py` is the glue holding everything together.

`convert.py` handles making MineOS `.lang` and `.cfg` files json-parsable and translating
entire files at once.

`translate.py` handles talking to Google Translate

`extricate.py` (name means taking apart and putting back together) is used by the translation
module to split dictionaries into a keys list and a values list so it can translate all the
values and then rebuild the dictionary by re-combining the keys list and the new translated
values list.

`agents.py` from https://github.com/Animenosekai/useragents/blob/main/pyuseragents/data/list.py
is by Anime no Sekai and has a ton of random user agents to use so Google Translate
doesn't get suspicious of us sending tens of thousands of requests without an API key

`languages.py` from https://github.com/ssut/py-googletrans/blob/master/googletrans/constants.py
is by ssut and has a giant dictionary of language names matched with ISO 639-1:2002 language codes
