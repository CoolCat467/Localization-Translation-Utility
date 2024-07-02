"""CSV Translate - Translate the Nanosaur Strings CSV file."""

# Programmed by CoolCat467

from __future__ import annotations

# CSV Translate - Translate the Nanosaur Strings CSV file.
# Copyright (C) 2023-2024  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__title__ = "CSV Translate"
__author__ = "CoolCat467"
__version__ = "0.0.0"
__license__ = "GNU General Public License Version 3"


import csv
import io
import os

import httpx
import trio
from localization_translation import translate
from localization_translation.languages import LANGUAGES


def raw_github_address(user: str, repo: str, branch: str, path: str) -> str:
    """Get raw GitHub user content URL of a specific file."""
    return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"


def nanosaur_url(path: str) -> str:
    """Return raw GitHub address to path from MineOS repository."""
    return raw_github_address("jorio", "Nanosaur2", "master", path)


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


async def download_coroutine(client: httpx.AsyncClient, url: str) -> bytes:
    """Return the sentence translated, asynchronously."""
    # Go to the URL and get response
    response = await client.get(url, follow_redirects=True)
    if not response.is_success:
        response.raise_for_status()
    # Wait for our response
    return await response.aread()


async def download_file(path: str, cache_dir: str, client: httpx.AsyncClient) -> str:
    """Download file at path from Nanosaur2 repository."""
    real_path = os.path.join(cache_dir, *path.split("/"))
    if not os.path.exists(real_path):
        ensure_folder_exists(real_path)
        print(f"GET {path}")
        response = await download_coroutine(client, nanosaur_url(path))
        ##        j_resp = json.loads(response)
        ##        data = base64.b64decode(j_resp['content'])
        with open(real_path, "wb") as file:
            file.write(response)
        await trio.sleep(1)
        return response.decode("utf-8")
    print(f"Loaded {path} from cache")
    with open(real_path, encoding="utf-8") as file:
        return file.read()


async def translate_file(
    sentences: list[str],
    client: httpx.AsyncClient,
    to_lang: str,
    src_lang: str = "auto",
) -> list[str]:
    """Translate an entire file."""
    insert: dict[int, str] = {}
    modified: list[str] = []
    for idx, value in enumerate(sentences):
        if value in {"{", ""}:
            insert[idx] = value
            continue
        modified.append(value)
    results: list[str] = await translate.translate_async(client, modified, to_lang, src_lang)
    for idx, value in insert.items():
        results.insert(idx, value)
    for old, new in zip(enumerate(sentences), results, strict=True):
        idx, orig = old
        if orig.endswith(" ") and not new.endswith(" "):
            results[idx] = new + " "
        elif orig.endswith(".") and not new.endswith("."):
            results[idx] = new + "."
    return results


class Nanosaur(csv.Dialect):
    """Nanosaur dialect."""

    delimiter = ","
    doublequote = False
    escapechar = None
    lineterminator = "\r\n"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    skipinitialspace = False


csv.register_dialect("nanosaur", Nanosaur)


def read_nanosaur_localization(csv_file: io.StringIO) -> dict[str, list[str]]:
    """Read nanosaur localization file."""
    header = csv_file.readline().strip()
    assert isinstance(header, str)
    names = header.split(",")
    reader = csv.reader(csv_file, dialect="nanosaur")
    languages: dict[str, list[str]] = {name: [] for name in names}
    for _ in zip(range(len(names)), reader, strict=False):
        continue
    for row in reader:
        if not row:
            continue
        ##            print(row)
        for i, value in enumerate(row):
            if not value:
                for j in range(i, -1, -1):
                    if value := row[j]:
                        break
            languages[names[i]].append(value)
    return languages


def write_nanosaur_localization(filename: str, languages: dict[str, list[str]]) -> None:
    """Write nanosaur localization file."""
    with open(filename, "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, dialect="nanosaur")
        names = list(languages)
        writer.writerow(names)
        lang_count = len(names)
        for lang in names:
            writer.writerow([lang] + [""] * (lang_count - 1))
        for line in range(len(languages[names[0]])):
            row = []
            last = ""
            for i in range(lang_count):
                value = languages[names[i]][line]
                if value != last:
                    row.append(value)
                else:
                    row.append("")
                last = value
            writer.writerow(row)


async def create_translation(languages: dict[str, list[str]], code: str, client: httpx.AsyncClient) -> None:
    """Add translation for language with given code to languages dictionary."""
    result = await translate_file(languages["English"], client, code, "en")
    title = LANGUAGES[code].title()
    languages[title] = result
    print(f"Translated to {title}")


async def async_run() -> None:
    """Run program."""
    cache = os.path.join(os.path.split(__file__)[0], "cache")
    async with httpx.AsyncClient(http2=True) as client:
        contents = await download_file("Data/System/strings.csv", cache, client)
        file = io.StringIO(contents)
        languages = read_nanosaur_localization(file)
        file.close()

        async with trio.open_nursery() as nursery:
            for code in ("pl", "be"):
                nursery.start_soon(create_translation, languages, code, client)
    print("Saving result to Upload/strings.csv")
    write_nanosaur_localization("Upload/strings.csv", languages)


def run() -> None:
    """Translate nanosaur strings."""
    trio.run(async_run)


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.")
    run()
