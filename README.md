# Localization-Translation-Utility
Script for simplifying the process of translating Language (.lang) files

<!-- BADGIE TIME -->

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/CoolCat467/Localization-Translation-Utility/main.svg)](https://results.pre-commit.ci/latest/github/CoolCat467/Localization-Translation-Utility/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![code style: black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- END BADGIE TIME -->

Supports MineOS lang files, which is the main purpose of this project's existence

Simply run `auto_trans.py` and everything else except fixing comment positions is done.

The program will download `Installer/Files.cfg` from MineOS repo, save downloaded files
to `cache` folder it creates, and then for every language code in `languages.py` (from
https://github.com/ssut/py-googletrans/blob/master/googletrans/constants.py)
it will use google translate with different user agents from `agents.py` (from
https://github.com/Animenosekai/useragents/blob/main/pyuseragents/data/list.py) to translate
the English localization to that language and save the new file in the `Upload` folder
it creates.

WARNING: Creating hundreds of new files takes up a lot of space on your computer!
This program may require more than 3.5 MB to store the new localizations alone!


General code layout:

`auto_trans.py` is the glue holding everything together, and is what you run as the main script.

`convert.py` handles making MineOS `.lang` and `.cfg` files json-parsable and translating
entire files at once.

`translate.py` handles talking to Google Translate

`agents.py` from https://github.com/Animenosekai/useragents/blob/main/pyuseragents/data/list.py
is by Anime no Sekai and has a ton of random user agents to use so Google Translate
doesn't get suspicious of us sending tens of thousands of requests without an API key

`languages.py` from https://github.com/ssut/py-googletrans/blob/master/googletrans/constants.py
is by ssut and has a giant dictionary of language names matched with ISO 639-1:2002 language codes



Versions:
1.0.0 - Initial release

2.0.0 - Adding auto translation and general clean-up

3.0.0 - Automate everything except fixing comment positions.

3.1.0 - Fix comment positions.

4.0.0 - Change to trio instead of asyncio and add ability to fix single untranslated value.

4.1.0 - Add ability to fix untranslated values in all localization files
