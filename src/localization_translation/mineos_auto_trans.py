#!/usr/bin/env python3
# Auto Translate localization files for MineOS

"""Auto Translate localization files for MineOS."""

# Programmed by CoolCat467

__title__ = "Auto_Trans"
__author__ = "CoolCat467"
__version__ = "2.2.0"
__ver_major__ = 2
__ver_minor__ = 2
__ver_patch__ = 0

import copy
import os
from collections.abc import Awaitable, Callable
from typing import Any

import convert
import extricate
import httpx
import languages
import lolcat
import translate
import trio

##import json
##import base64
##import time


##def raw_github_address(user: str, repo: str, branch: str, path: str) -> str:
##    "Get raw github user content url of a specific file."
####    return f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}'
##    return f'https://api.github.com/repos/{user}/{repo}/contents/{path}'
##
##async def download_coroutine(client: httpx.AsyncClient, url: str) -> bytes:
##    "Return the sentence translated, asynchronously."
##    # Go to the url and get response
##    response = await client.get(url, follow_redirects=True)
##    if 'x-Ratelimit-Remaining' in response.headers:
##        still = response.headers['X-RateLimit-Reset']
##        print(f'Requests Remaining: {still}')
##    if 'X-RateLimit-Reset' in response.headers:
##        delay = round(int(response.headers['X-RateLimit-Reset']) - time.time())
##        print(f'Rate limiting resets in {timeutils.format_time(delay)}')
##    if not response.is_success:
##        response.raise_for_status()
##    # Wait for our response
##    return await response.aread()


async def translate_file(data: dict, client: httpx.AsyncClient, to_lang: str, src_lang: str = "auto") -> dict:
    """Translate an entire file."""
    keys, sentences = extricate.dict_to_list(data)
    results = await translate.translate_async(client, sentences, to_lang, src_lang)
    for old, new in zip(enumerate(sentences), results, strict=True):
        idx, orig = old
        if new is None or not isinstance(orig, str):
            results[idx] = orig
        elif orig.endswith(" ") and not new.endswith(" "):
            results[idx] = new + " "
    return extricate.list_to_dict(keys, results)  # type: ignore


def raw_github_address(user: str, repo: str, branch: str, path: str) -> str:
    """Get raw GitHub user content URL of a specific file."""
    return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"


async def download_coroutine(client: httpx.AsyncClient, url: str) -> bytes:
    """Return the sentence translated, asynchronously."""
    # Go to the URL and get response
    response = await client.get(url, follow_redirects=True)
    if not response.is_success:
        response.raise_for_status()
    # Wait for our response
    return await response.aread()


def mineos_url(path: str) -> str:
    """Return raw GitHub address to path from MineOS repository."""
    return raw_github_address("IgorTimofeev", "MineOS", "master", path)


def ensure_folder_exists(new_filename: str) -> None:
    """Ensure folder chain for new filename exists."""
    if os.path.exists(new_filename):
        return
    new_filename = os.path.abspath(new_filename)
    path = (os.path.split(new_filename)[0]).split(os.path.sep)
    for i in range(2, len(path) + 1):
        new_path = os.path.sep.join(path[:i])
        if not os.path.exists(new_path):
            os.mkdir(new_path)


##async def download_file(path: str, cache_dir: str, client: httpx.AsyncClient) -> str:
##    "Download file at path from MineOS repository."
##    real_path = os.path.join(cache_dir, *path.split('/'))
##    if not os.path.exists(real_path):
##        ensure_folder_exists(real_path)
##        print(f'GET {path}')
##        response = await download_coroutine(client, mineos_url(path))
##        j_resp = json.loads(response)
##        data = base64.b64decode(j_resp['content'])
##        with open(real_path, 'wb') as file:
##            file.write(data)
##        await trio.sleep(1)
##        return data.decode('utf-8')
##    print(f'Loaded {path} from cache')
##    with open(real_path, 'r', encoding='utf-8') as file:
##        return file.read()


async def download_file(path: str, cache_dir: str, client: httpx.AsyncClient) -> str:
    """Download file at path from MineOS repository."""
    real_path = os.path.join(cache_dir, *path.split("/"))
    if not os.path.exists(real_path):
        ensure_folder_exists(real_path)
        print(f"GET {path}")
        response = await download_coroutine(client, mineos_url(path))
        # j_resp = json.loads(response)
        # data = base64.b64decode(j_resp['content'])
        with open(real_path, "wb") as file:  # noqa: ASYNC101
            file.write(response)
        await trio.sleep(1)
        return response.decode("utf-8")
    print(f"Loaded {path} from cache")
    with open(real_path, encoding="utf-8") as file:  # noqa: ASYNC101
        return file.read()


async def download_lang(path: str, cache_dir: str, client: httpx.AsyncClient) -> tuple[dict, dict]:
    """Download file from MineOS repository and decode as lang file. Return dict and comments."""
    return convert.lang_to_json(await download_file(path, cache_dir, client))


def split(path: str) -> tuple[str, str]:
    """Split a path name.  Returns tuple "(head, tail)" where "tail" is
    everything after the final slash.  Either part may be empty.
    """
    data = path.split("/")
    return "/".join(data[:-1]), data[-1]


def section_to_walk(section: list) -> tuple:
    """Return folder and files from section."""
    dirs: dict[str, list[str]] = {}
    for full_path in section:
        path, filename = split(full_path)
        if path not in dirs:
            dirs[path] = []
        dirs[path].append(filename)
    return tuple(dirs.items())


async def translate_file_given_coro(
    trans_coro: Callable[[dict[str, Any], str, str], Awaitable[dict[str, str]]],
    file: tuple[dict, dict],
    lang_data: list[tuple[str, str]],
    folder: str,
) -> int:
    """Translate a file for all languages in lang_data and save as filename from data."""
    # English and comments is file
    # to_lang and filename is each entry in lang_data
    english, comments = file

    changed = 0

    async def translate_file_coro(to_lang: str, filename: str) -> None:
        """Translate file from English to to_lang, save as filename."""
        nonlocal changed
        # print(f"START {to_lang.title()}")
        new_lang = await trans_coro(english, to_lang, folder)
        if new_lang:
            print(f"END {to_lang.title()}")
            ensure_folder_exists(filename)
            convert.write_lang_file(filename, new_lang, comments)
            changed += 1
        else:
            print(f"END {to_lang.title()}: not changed")

    async with trio.open_nursery() as nursery:
        for to_lang, filename in lang_data:
            nursery.start_soon(translate_file_coro, to_lang, filename)
    return changed


async def abstract_translate(
    client: httpx.AsyncClient,
    base_lang: str,
    cache_folder: str,
    get_unhandled: Callable[[set[str], str], set[str]],
    trans_coro: Callable[[dict[str, Any], str, str], Awaitable[dict[str, str]]],
) -> None:
    """Main translate."""
    ignore_languages = {
        "chinese (traditional)",
    }
    convert_name = {"zh-cn": "chinese"}

    print("\nGettting files...")
    files, file_comments = await download_lang("Installer/Files.cfg", cache_folder, client)
    # Get true copy
    orig_files = copy.deepcopy(files)

    search: set[str] = set()
    for section, data in files.items():
        for entry in data:
            if isinstance(entry, str) and entry.endswith("English.lang"):
                search.add(section)

    print(f'\nSections with English.lang files: {", ".join(search)}\n')

    new_files = 1

    for section in search:
        lang_files = [f for f in files[section] if isinstance(f, str) and f.endswith(".lang")]
        if section == "localizations":
            lang_files += [f"Installer/{f}" for f in lang_files]
        if not lang_files:
            continue
        print("#" * 0x20 + section + "#" * 0x20)
        for folder, exists in section_to_walk(lang_files):
            handled_langs: set[str] = {(f.split(".")[0]).lower() for f in exists}
            if not handled_langs:
                continue
            last_handled = folder + "/" + exists[-1].split(".")[0].title() + ".lang"
            handled_langs |= ignore_languages

            unhandled = get_unhandled(handled_langs, folder)

            if not unhandled:
                print("All translations exist for this folder, skipping.")
                continue

            english, comments = await download_lang(f"{folder}/English.lang", cache_folder, client)

            real_folder = os.path.sep.join(folder.split("/"))
            base_group = os.path.join(base_lang, real_folder)
            total = len(unhandled)
            print(f"\n{total} languages do not exist, translating them now!")
            # print(f'{lang_files = }')
            insert_start = lang_files.index(last_handled)
            # insert_start = files[section].index(last_handled)

            lang_data = []

            for idx, to_lang in enumerate(unhandled):
                name = convert_name.get(to_lang, to_lang).title()

                fname = name.replace(" ", "_")
                fname = fname.replace("(", "").replace(")", "")
                section_filename = f"{folder}/{fname}.lang"
                if section_filename not in files[section]:
                    if folder == "Installer/Localizations":
                        continue
                    files[section].insert(insert_start + idx, section_filename)

                real_filename = os.path.join(base_group, f"{fname}.lang")
                if not os.path.exists(real_filename):
                    lang_data.append((to_lang, real_filename))
                else:
                    new_files += 1

            new_files += await translate_file_given_coro(trans_coro, (english, comments), lang_data, folder)
            print("\n" + "#" * 0xF + "Done with folder" + "#" * 0xF)
    print("\nLanguages have been translated and saved to upload folder!")

    if files == orig_files:
        new_files -= 1
    else:
        print("Writing Installer/Files.cfg...")
        file_list_filename = os.path.join(base_lang, "Installer", "Files.cfg")
        file_comments = convert.update_comment_positions(file_comments, files, orig_files)
        ensure_folder_exists(file_list_filename)
        convert.write_lang_file(file_list_filename, files, file_comments)

    print(f"Done! {new_files} new files created.")


async def translate_main(client: httpx.AsyncClient) -> None:
    """Translate with google translate."""
    here_folder = os.path.split(__file__)[0]
    base_lang = os.path.join(here_folder, "Upload")
    cache_folder = os.path.join(here_folder, "cache")

    def get_unhandled(handled: set, folder: str) -> set[str]:
        # return [v for k, v in languages.LANGCODES.items() if not k in handled]
        # return ['greek']
        return {k for k in languages.LANGCODES if k not in handled}

    async def trans_coro(english: dict, to_lang: str, folder: str) -> dict:
        code = languages.LANGCODES[to_lang]
        return await translate_file(english, client, code, "en")

    await abstract_translate(client, base_lang, cache_folder, get_unhandled, trans_coro)


async def translate_new_value(client: httpx.AsyncClient, key: str, folder: str) -> None:
    """Translate with google translate."""
    here_folder = os.path.split(__file__)[0]
    base_lang = os.path.join(here_folder, "Upload")
    cache_folder = os.path.join(here_folder, "cache")

    def get_unhandled(handled: set, lang_folder: str) -> set[str]:
        if lang_folder == folder:
            return handled.difference({"chinese (traditional)", "english", "lolcat"})
        return set()

    async def trans_coro(english: dict, to_lang: str, folder: str) -> dict:
        fname = to_lang.replace(" ", "_")
        fname = fname.replace("(", "").replace(")", "").title()
        filename = f"{folder}/{fname}.lang"

        data = (await download_lang(filename, cache_folder, client))[0]

        if to_lang == "chinese":
            to_lang += " (traditional)"

        code = languages.LANGCODES[to_lang]

        values = await translate.translate_async(client, [english[key]], code, "en")
        data[key] = values[0]
        return data

    await abstract_translate(client, base_lang, cache_folder, get_unhandled, trans_coro)


def fix_translation(original: str, value: str) -> str:
    """Fix translation."""
    if original.strip()[0].isupper() and " " in value:
        pre, end = value.split(" ", 1)
        value = f"{pre.title()} {end}"
    if original.startswith(" ") and not value.startswith(" "):
        value = " " + value
    if original.endswith(" ") and not value.endswith(" "):
        value += " "
    if original in {" mm Hg", "http://example.com/something.lua"}:
        return original
    return value


async def translate_broken_values(client: httpx.AsyncClient) -> None:
    """Translate with google translate."""
    here_folder = os.path.split(__file__)[0]
    base_lang = os.path.join(here_folder, "Upload")
    cache_folder = os.path.join(here_folder, "cache")

    def get_unhandled(handled: set[str], lang_folder: str) -> set[str]:
        if "Localizations" not in lang_folder:
            return set()
        return handled.difference({"chinese (traditional)", "english", "lolcat"})

    async def trans_coro(english: dict, to_lang: str, folder: str) -> dict:
        fname = to_lang.replace(" ", "_")
        fname = fname.replace("(", "").replace(")", "").title()
        filename = f"{folder}/{fname}.lang"

        data = (await download_lang(filename, cache_folder, client))[0]

        if to_lang == "chinese":
            to_lang += " (traditional)"

        code = languages.LANGCODES[to_lang]

        ##        translated = await translate_file(english, client, code, 'en')
        async def translate_single(key: str) -> None:
            """Translate single value."""
            ##            print(f'{english[key] = }')
            if not isinstance(english[key], str):
                return
            value = await translate.get_translated_coroutine(client, english[key], code, "en")
            value = fix_translation(english[key], value)
            if value != data[key]:
                print(f"{data[key]!r} -> {value!r}")
            data[key] = value

        modified = False
        async with trio.open_nursery() as nursery:
            for key in data:
                if data[key] == english[key] or key == data[key]:
                    # print(f'{data[key]!r} -> {translated[key]!r}')
                    # data[key] = translated[key]
                    nursery.start_soon(translate_single, key)
                    modified = True

        if modified:
            return data
        return {}

    await abstract_translate(client, base_lang, cache_folder, get_unhandled, trans_coro)


async def translate_lolcat(client: httpx.AsyncClient) -> None:
    """Translate with website."""
    # https://funtranslations.com/lolcat

    here_folder = os.path.split(__file__)[0]
    base_lang = os.path.join(here_folder, "Upload")
    cache_folder = os.path.join(here_folder, "cache")

    def get_unhandled(handled: set[str], folder: str) -> set[str]:
        return {"lolcat"}  # if not 'lolcat' in handled else set()

    async def trans_coro(english: dict, to_lang: str, folder: str) -> dict:
        return lolcat.translate_file(english)

    await abstract_translate(client, base_lang, cache_folder, get_unhandled, trans_coro)


async def async_run() -> None:
    """Async entry point."""
    async with httpx.AsyncClient(http2=True) as client:
        # await translate_main(client)
        await translate_broken_values(client)

        # await translate_new_value(client, 'screenPreciseMode', 'Applications/Settings.app/Localizations')
        # await translate_new_value(client, 'categoryWallpapers', 'Applications/App Market.app/Localizations')
        # await translate_lolcat(client)


def run() -> None:
    """Main entry point."""
    # import trio.testing
    trio.run(async_run, strict_exception_groups=True)
    # , clock=trio.testing.MockClock(autojump_threshold=0))


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.")
    run()
