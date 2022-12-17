#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Lexer - Read text and convert to tokens

"Lexer"

# Programmed by CoolCat467

__title__ = 'Lexer'
__author__ = 'CoolCat467'
__version__ = '0.0.0'

from typing import Iterable, Iterator

from collections import deque

import re

class Token:
    "Lexer Token class"
    def __init__(self,
                 token_type: str | int,
                 regex: re.Pattern | str) -> None:
        self.type = token_type
        if not isinstance(regex, re.Pattern):
            self.regex = re.compile(regex)
        else:
            self.regex = regex
    
    def match(self, text: str) -> tuple[None | str, str]:
        "Match text with regular expression and return match result and non-matching text"
        result = self.regex.match(text)
        if result is None:
            return result, text
        end = result.end()
        return text[:end], text[end:]
    
    def __repr__(self) -> str:
        return f'Token({self.type!r}, {self.regex!r})'

class Lexer:
    "Text lexer"
    __slots__ = ('tokens', 'input')
    def __init__(self) -> None:
        self.tokens: set[Token] = set()
        self.input: deque[str] = deque()
    
    def add_token(self, token: Token) -> None:
        "Add token to lexer"
        if not isinstance(token, Token):
            raise ValueError('New token is not instance of Token class!')
        self.tokens.add(token)
    
    def add_tokens(self, tokens: Iterable[Token]) -> None:
        "Add multiple tokens to lexer"
        for token in tokens:
            self.add_token(token)
    
    def read_input(self, text: str) -> None:
        "Add text to input"
        self.input.extend(text)
    
    def input_gen(self) -> Iterator[str]:
        "Yield characters from input"
        while self.input:
            yield self.input.popleft()
    
    def word_gen(self) -> Iterator[str]:
        "Yield words from input"
        word = ''
        for char in self.input_gen():
            if char == ' ':
                yield word
                word = ''
                continue
            word += char
        if word:
            yield word
    
    def lex_input(self) -> Iterator[tuple[str | int | None, str]]:
        "Yield token type and matched text. Unhandled type is None."
        for word in self.word_gen():
            for token in self.tokens:
                match, extra = token.match(word)
                if match is not None:
                    if extra:
                        self.input.extendleft(reversed(extra+' '))
                    yield token.type, match
                    break
            else:
                yield None, word
        if self.input:
            for token_type, word in self.lex_input():
                yield token_type, word
    


def run() -> None:
    "Run test of module"
    test = Lexer()
    
    test.add_token(Token('text', re.compile('[a-z|A-Z]+')))
##    test.add_token(Token('other', '![a-z|A-Z]+'))
    test.add_token(Token('number', re.compile('[0-9]+')))
    
    test.read_input('This cat video234cat is fire 12345 woo')
    
    for token_type, text in test.lex_input():
        print(f'{token_type}: {text}')




if __name__ == '__main__':
    print(f'{__title__}\nProgrammed by {__author__}.\n')
    run()
