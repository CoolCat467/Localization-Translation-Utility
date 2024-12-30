"""Lexer - Read text and convert to tokens."""

# Programmed by CoolCat467

from __future__ import annotations

# Lexer - Read text and convert to tokens
# Copyright (C) 2022-2024  CoolCat467
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

__title__ = "Lexer"
__author__ = "CoolCat467"
__version__ = "0.0.0"
__license__ = "GNU General Public License Version 3"


import re
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class Token:
    """Lexer Token class."""

    __slots__ = ("regex", "type")

    def __init__(self, token_type: str | int, regex: re.Pattern[str] | str) -> None:
        """Initialize Token."""
        self.type = token_type
        if not isinstance(regex, re.Pattern):
            self.regex = re.compile(regex)
        else:
            self.regex = regex

    def __repr__(self) -> str:
        """Return representation of self."""
        return f"Token({self.type!r}, {self.regex!r})"

    def match(self, text: str) -> tuple[None | str, str]:
        """Match text with regular expression and return match result and non-matching text."""
        result = self.regex.match(text)
        if result is None:
            return result, text
        end = result.end()
        return text[:end], text[end:]


class Lexer:
    """Text lexer."""

    __slots__ = ("input", "tokens")

    def __init__(self) -> None:
        """Initialize Lexer."""
        self.tokens: set[Token] = set()
        self.input: deque[str] = deque()

    def add_token(self, token: Token) -> None:
        """Add token to lexer."""
        if not isinstance(token, Token):
            raise ValueError("New token is not instance of Token class!")
        self.tokens.add(token)

    def add_tokens(self, tokens: Iterable[Token]) -> None:
        """Add multiple tokens to lexer."""
        for token in tokens:
            self.add_token(token)

    def read_input(self, text: str) -> None:
        """Add text to input."""
        self.input.extend(text)

    def input_gen(self) -> Iterator[str]:
        """Yield characters from input."""
        while self.input:
            yield self.input.popleft()

    def word_gen(self) -> Iterator[str]:
        """Yield words from input."""
        word = ""
        for char in self.input_gen():
            if char == " ":
                yield word
                word = ""
                continue
            word += char
        if word:
            yield word

    def lex_input(self) -> Iterator[tuple[str | int | None, str]]:
        """Yield token type and matched text. Unhandled type is None."""
        for word in self.word_gen():
            for token in self.tokens:
                match, extra = token.match(word)
                if match is not None:
                    if extra:
                        self.input.extendleft(reversed(extra + " "))
                    yield token.type, match
                    break
            else:
                yield None, word
        if self.input:
            for token_type, word in self.lex_input():
                yield token_type, word


def run() -> None:
    """Run test of module."""
    test = Lexer()

    test.add_token(Token("text", re.compile("[a-z|A-Z]+")))
    ##    test.add_token(Token('other', '![a-z|A-Z]+'))
    test.add_token(Token("number", re.compile("[0-9]+")))

    test.read_input("This cat video234cat is fire 12345 woo")

    for token_type, text in test.lex_input():
        print(f"{token_type}: {text}")


if __name__ == "__main__":
    print(f"{__title__}\nProgrammed by {__author__}.\n")
    run()
