"""Lua Convert Parser - Properly parse lua and rebuild perfectly, no more json shenanigins."""

# Programmed by CoolCat467

from __future__ import annotations

# Lua Convert Parser - Properly parse lua and rebuild perfectly, no more json shenanigins
# Copyright (C) 2024  CoolCat467
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

__title__ = "Lua Convert Parser"
__author__ = "CoolCat467"
__version__ = "0.0.0"
__license__ = "GNU General Public License Version 3"

from enum import IntEnum, auto
from typing import Any, NamedTuple

from localization_translation import lua_parser


class TokenType(IntEnum):
    """Token types for comment data tokens."""

    Separator = auto()
    Newline = auto()
    Whitespace = auto()
    Identifier = auto()
    Numeric = auto()
    Comment = auto()
    StartBracket = auto()
    EndBracket = auto()


class Token(NamedTuple):
    """Comment token data."""

    type_: TokenType
    text: str = ""


class CommentData(NamedTuple):
    """Comment data collection."""

    indentation: tuple[IndentFormat, ...]
    keys: tuple[Token, ...]


class IndentFormat(NamedTuple):
    """Indentation format data."""

    multiline: bool  # Compressed, all one line, or multiline?
    indent_text: str  # Text to use for indentation per line or prefix/suffix if compressed


def lang_to_json(
    lang_data: str,
) -> tuple[dict[str, Any], CommentData]:
    """Fix language data to be readable by json parser. Return data and comments."""
    all_tokens: list[lua_parser.Token] = list(lua_parser.tokenize_cst(lang_data))
    parser = lua_parser.Parser([t for t in all_tokens if not isinstance(t, lua_parser.CSTToken)])
    table_value = parser.parse_value()
    data, read_tokens = lua_parser.parse_lua_table(table_value, False)
    assert isinstance(data, dict)

    indent_format: list[IndentFormat] = []
    key_data: list[Token] = []

    i = -1

    def next_token() -> lua_parser.Token:
        nonlocal i
        i += 1
        if i >= len(all_tokens):
            raise ValueError("Reached EOF")
        return all_tokens[i]

    while i < (len(all_tokens) - 1):
        token = next_token()
        text = token.text
        if isinstance(token, lua_parser.Separator):
            if text == "{":
                key_data.append(Token(TokenType.StartBracket))
                multiline = False
                indent_text = " "
                token = next_token()
                if isinstance(token, lua_parser.Newline):
                    multiline = True
                    token = next_token()
                if isinstance(token, lua_parser.Whitespace):
                    indent_text = token.text
                indent_format.append(IndentFormat(multiline, indent_text))
            elif text == ",":
                if not isinstance(next_token(), lua_parser.Newline):
                    i -= 1
            elif text == "}":
                if key_data[-1].type_ == TokenType.Newline and key_data[-2].type_ == TokenType.Identifier:
                    del key_data[-1]
                key_data.append(Token(TokenType.EndBracket))
                if not isinstance(next_token(), lua_parser.Newline):
                    i -= 1
        elif isinstance(token, lua_parser.Identifier):
            key_data.append(Token(TokenType.Identifier, token.text))
        elif isinstance(token, lua_parser.Numeric):
            key_data.append(Token(TokenType.Numeric, token.text))
        elif isinstance(token, lua_parser.Comment):
            key_data.append(Token(TokenType.Comment, token.text))
            if not isinstance(next_token(), lua_parser.Newline):
                i -= 1
        elif isinstance(token, lua_parser.Newline):
            key_data.append(Token(TokenType.Newline))
        elif isinstance(token, lua_parser.Assignment):
            token = next_token()
            while isinstance(token, lua_parser.Whitespace):
                token = next_token()
            if not isinstance(token, lua_parser.Numeric):
                i -= 1
                print(f"{token = }")

    return data, CommentData(tuple(indent_format), tuple(key_data))


def dict_to_lang(
    data: dict[str, Any],
    comments: CommentData,
) -> str:
    """Convert data and comments to MineOS file data."""
    ##    print(f'{comments.indentation}')
    print(f"{comments.keys}")

    indentation = list(comments.indentation)

    line = ""
    lines: list[str] = []

    ##    def write_dict(keys: list[lua_parser.Token]) -> None:
    ##        nonlocal line
    indent_queue: list[IndentFormat] = []
    indent = IndentFormat(True, "")

    def cartrage_return() -> None:
        nonlocal line
        if indent.multiline:
            lines.append(line.rstrip())
            line = ""
        line += indent.indent_text

    root: dict[str | int, Any] = data
    roots: list[dict[str | int, Any]] = []
    last_key: str | int | None = None

    in_blocks = 0
    has_keys = False
    in_unmarked = False
    unmarked_index = 1
    unmarked_groups: list[tuple[bool, int]] = []

    for idx, token in enumerate(comments.keys):
        if token.type_ == TokenType.StartBracket:
            in_blocks += 1
            in_unmarked = not has_keys
            unmarked_groups.append((in_unmarked, unmarked_index))
            has_keys = False
            roots.append(root)
            if last_key is not None:
                if in_unmarked:
                    last_key = unmarked_index
                if last_key not in root:
                    print("\n".join([*lines, line]))
                root = root[last_key]
            line += "{"
            indent_queue.append(indent)
            indent = indentation.pop(0)
            ##                print(f'{indent = }')
            cartrage_return()
        elif token.type_ == TokenType.EndBracket:
            in_blocks -= 1
            in_unmarked, unmarked_index = unmarked_groups.pop()
            has_keys = not in_unmarked
            if not in_unmarked:
                unmarked_index = 1
            else:
                unmarked_index += 1
            root = roots.pop()
            last_indent = indent
            indent = indent_queue.pop()
            ##                print(f'{line = }')
            ##                print(f'{indent = }\n')
            if last_indent.multiline:
                line = indent.indent_text
            ##                cartrage_return()
            line += "}"
            if in_blocks > 0:
                line += ","
            cartrage_return()
        elif token.type_ == TokenType.Newline:
            cartrage_return()
        elif token.type_ in {TokenType.Identifier, TokenType.Numeric}:
            has_keys = True
            last_key = token.text
            if token.type_ == TokenType.Numeric:
                line += f"[{token.text}]"
                last_key = int(last_key)
            else:
                line += token.text
            line += " = "
            if comments.keys[idx + 1].type_ != TokenType.StartBracket:
                assert isinstance(root[last_key], str | int | float), "should not unpack collections"
                value = root[last_key]
                if isinstance(value, int | float):
                    line += repr(root[last_key])
                else:
                    line += f'"{value}"'
                if comments.keys[idx + 1].type_ != TokenType.EndBracket:
                    line += ","
                cartrage_return()
        elif token.type_ == TokenType.Comment:
            line += token.text
            cartrage_return()
        elif token.type_ == TokenType.Whitespace:
            line += token.text
    ##        elif isinstance(token, lua_parser.Separator):
    ##            line += token.text

    ##    write_dict(comments.keys)

    return "\n".join(lines)


def run() -> None:
    """Run program."""
    text = """{
	leftBarOffset = 5,

	settingsStyle = "Color scheme",
	settingsAdditional = "Additional properties",

	invalidPassword = "Invalid login or password",
	username = "E-mail or phone number",
	password = "Password",
	login = "Enter",
	twoFactorEnabled = "Use 2FA",
	twoFactor = "2FA code",
	saveLogin = "Save login information:",

	loadCountConversations = "The number of loaded dialogues",
	loadCountMessages = "Number of messages to download",
	loadCountNews = "Number of downloaded news",
	scrollSpeed = "The scroll speed",
	loadCountWall = "Number of posts to download",
	loadCountFriends = "Number of friends to download",
	loadCountDocs = "Number of documents to download",

	profile = "Profile",
	message = "Message",
	sendMessage = "Send message",
	addToFriends = "Add as friend",
	friendRequestSent = "Request has been sent",
	userSubscribedToYou = "Subscribed to you",
	userIsYourFriend = "You have friends",

	profileCounters = {
		{ field = "followers", description = " followers" },
		{ field = "friends", description = " friends" },
		{ field = "photos", description = " photos" },
		{ field = "videos", description = " videos" },
		{ field = "audios", description = " audio" },
	},
	profileShowAdditional = "Show details",
	profileHideAdditional = "Hide detailed information",
	profileTitleMainInformation = "Basic information",
	profileTitlePersonal = "Life position",
	profileTitleAdditions = "Personal information",
	profileTitleContacts = "Contacts",
	profileKeys = {
		education = "Education",
		inspiredBy = "Inspire",
		relation = "Relations",
		birthday = "Birthday",
		city = "City",
		homeCity = "Hometown",
		languages = "Languages",
		occupation = "Place of work",
		mobilePhone = "Mobile",
		homePhone = "Alt. phone",
		site = "Website",
		activities = "Activity",
		interests = "Interests",
		music = "Favorite music",
		movies = "Favorite movie",
		books = "Favorite book",
		tv = "Favorite show",
		games = "Favorite game",
		quotes = "Favorite quote",
		religion = "Outlook",
		political = "Polit. conviction",
		peopleMain = "People most important",
		lifeMain = "Life most important",
		alcohol = "OTN. for alcohol",
		smoking = "OTN. towards smoking",
	},
	months = {
		"january",
		"february",
		"march",
		"april",
		"may",
		"june",
		"july",
		"august",
		"september",
		"october",
		"november",
		"december",
	},
	relationStatuses = {
		{
			"not married",
			"have a girlfriend",
			"engaged",
			"married",
			"it's complicated",
			"in active search",
			"lover",
			"in civil marriage",
			[0] = "unspecified",
		},
		{
			"not married",
			"have a friend",
			"engaged",
			"married",
			"it's complicated",
			"in active search",
			"lover",
			"in civil marriage",
			[0] = "unspecified",
		}
	},
	personalPoliticalTypes = {
		"Communist",
		"Socialist",
		"Moderate",
		"Liberal",
		"Conservative",
		"Monarchical",
		"Ultraconservative",
		"Indifferent",
		"Libertarian",
	},
	personalPeopleMainTypes = {
		"Intelligence and creativity",
		"Kindness and honesty",
		"Beauty and health",
		"Power and wealth",
		"Courage and perseverance",
		"Humor and love of life",
	},
	personalLifeMainTypes = {
		"Family and children",
		"Career and money",
		"Entertainment and recreation",
		"Science and research",
		"Improving the world",
		"Self-development",
		"Beauty and art",
		"Fame and influence",
	},
	personalBlyadTypes = {
		"Sharply negative",
		"Negative",
		"Compromise",
		"Neutral",
		"Positive",
	},

	friends = "Friends",
	friendsOnline = "Online friends",
	friendsMutual = "Mutual friends",

	news = "Newsfeed",

	send = "Send",
	conversations = "Conversations",
	you = "You: ",
	typeMessageHere = "Write a message...",
	fwdMessages = "Information: ",
	attachments = "Investments: ",
	attachmentsTypes = {
		photo = "photo",
		video = "video",
		audio = "audio",
		doc = "document",
		link = "link",
		market = "goods",
		market_album = "product catalog",
		wall = "record",
		wall_reply = "repost",
		sticker = "sticker",
		gift = "gift",
		audio_message = "audio",
	},
	sentFromMineOS = " (Sent via MineOS VK Client)",

	documents = "Documents",
	documentsCount = "Total documents",
	documentsAdd = "Upload document",

	settings = "Settings",

	exit = "Logout"
}"""
    data, comments = lang_to_json(text)
    print(data)
    ##    data['population'] = 'Jerald text: '
    ##    data['winds'][5] = 'Five'
    ##    data['cityError'] = 'City not found, please click again.'
    ##    print(comments.all_tokens)
    ##    print(comments.parse_tokens)
    result = dict_to_lang(data, comments)
    print(result)
    if data != result:
        from difflib import context_diff

        print(
            "".join(
                context_diff(text.splitlines(True), result.splitlines(True), fromfile="original", tofile="repackaged"),
            ),
            end="",
        )


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
    run()
