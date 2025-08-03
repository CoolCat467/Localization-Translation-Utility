"""Lua Parser."""

# Programmed by CoolCat467

from __future__ import annotations

# Lua Parser
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

__title__ = "Lua Parser"
__author__ = "CoolCat467"
__license__ = "GNU General Public License Version 3"


import re
from collections import deque
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    NamedTuple,
    NoReturn,
    TypeVar,
    cast,
)

if TYPE_CHECKING:
    from collections.abc import Collection, Generator


class ParseError(Exception):
    """Raised on any type comment parse error."""


class Token(NamedTuple):
    """Base token."""

    text: str
    line: int
    column: int

    @property
    def endcolumn(self) -> int:
        """End column number."""
        return self.column + len(self.text)

    @property
    def endline(self) -> int:
        """End line number."""
        return self.line + self.text.count("\n")

    def location(self) -> str:
        """Location of token."""
        return f"{self.line}:{self.column}"

    def selection(self) -> str:
        """Select location of token."""
        return f"{self.location()}:{self.endline}:{self.endcolumn}"


class Identifier(Token):
    """A lua identifier, such as a variable name."""

    __slots__ = ()


class Operator(Token):
    """Base class for all operator tokens."""

    __slots__ = ()


class Assignment(Operator):
    """A lua assignment operator."""

    __slots__ = ()


class Literal(Token):
    """Base literal."""

    __slots__ = ()


class StrLit(Literal):
    """String literal."""

    __slots__ = ()


class Numeric(Literal):
    """Numeric literal."""

    __slots__ = ()


class Separator(Token):
    """A separator or punctuator token such as braces or quotes."""

    __slots__ = ()


class End(Token):
    """A token representing the end."""

    __slots__ = ()


class CSTToken(Token):
    """Base class for all Concrete Syntax Tree tokens."""

    __slots__ = ()


class Whitespace(CSTToken):
    """A token representing whitespace."""

    __slots__ = ()


class Newline(CSTToken):
    """A token representing a newline."""

    __slots__ = ()


class Comment(CSTToken):
    """An entire comment line."""

    __slots__ = ()


KEYWORDS = {
    "and",
    "break",
    "do",
    "else",
    "elseif",
    "end",
    "false",
    "for",
    "function",
    "goto",
    "if",
    "in",
    "local",
    "nil",
    "not",
    "or",
    "repeat",
    "return",
    "then",
    "true",
    "until",
    "while",
}

IDENTIFIER = re.compile(r"^[a-z_][a-z_\d]*", re.IGNORECASE)
COMMENT = re.compile("--.*\n")
##INTEGER = re.compile('^[\d]+')
NUMERIC = re.compile(r"^-?(\d+)(\.\d+)?(e(?:-|\+)?\d+)?")
HEXADECIMAL = re.compile(
    r"(0x[a-f\d]+)(\.[a-f\d]+)?(p(?:-|\+)?\d+)?",
    re.IGNORECASE,
)


def tokenize_cst(text: str) -> Generator[Token, None, None]:
    """Tokenize lua code. Yields tokens and complex syntax tree tokens."""
    line = 1
    column = -1

    while True:
        read = 1
        last_line = line
        token: type[Token] | None = End

        if not text:
            read = 0
        elif text[0] in {" ", "\r", "\t"}:
            while read < len(text) and text[read] in {" ", "\r", "\t"}:
                read += 1
            token = Whitespace
        elif text[0] == "\n":
            token = Newline
            line += 1
        elif text[0] in "()[]{},;":
            token = Separator
        elif text.startswith("--"):
            match_ = COMMENT.match(text)
            if not match_:
                raise ParseError(f"Could not parse comment from {text!r}")

            token = Comment
            read = match_.end() - 1
        elif text[0] == "=":
            token = Assignment
        elif text[0] in {'"', "'"}:
            read = 1
            start_bracket = text[0]
            while read < len(text):
                char = text[read]
                if char == start_bracket and text[read - 1] != "\\":
                    read += 1
                    break
                read += 1

            token = StrLit
        else:
            if match_ := (HEXADECIMAL.match(text) or NUMERIC.match(text)):
                token = Numeric
                read = match_.end()
            elif match_ := IDENTIFIER.match(text):
                token = Identifier
                read = match_.end()
            else:
                raise ParseError(f"Could not parse {text!r}")

        if last_line != line:
            column = -1
        else:
            column += read

        if token is not None:
            yield token(text[:read], line, column)
            if issubclass(token, End):
                break
        text = text[read:]


def tokenize(text: str) -> Generator[Token, None, None]:
    """Tokenize lua code. Yields tokens."""
    for token in tokenize_cst(text):
        if isinstance(token, CSTToken):
            continue
        yield token


T = TypeVar("T")


class Value(Generic[T]):
    """A type value, potentially collection of multiple."""

    __slots__ = ("args", "from_token", "name")

    def __init__(
        self,
        name: str,
        *args: T,
        from_token: Token | None = None,
    ) -> None:
        """Set up name and arguments."""
        self.name = name
        if args:
            self.args = tuple(args)
        else:
            self.args = ()
        self.from_token = from_token

    def __repr__(self) -> str:
        """Return representation of self."""
        args = f", {self.args!r}" if self.args else ""
        from_ = ""
        if self.from_token is not None:
            from_ = f", from_token={self.from_token}"
        return f"{self.__class__.__name__}({self.name!r}{args}{from_})"

    def __str__(self) -> str:
        """Return type value representation of self."""
        if not self.args:
            return self.name or "[]"
        args = []
        for arg in self.args:
            if isinstance(arg, Value):
                args.append(str(arg))
            else:
                args.append(repr(arg))
        values = ", ".join(args)
        return f"{self.name}[{values}]"

    def __eq__(self, rhs: object) -> bool:
        """Return if rhs is equal to self."""
        if isinstance(rhs, self.__class__):
            return self.name == rhs.name and self.args == rhs.args
        return super().__eq__(rhs)

    def unpack(self) -> tuple[T | tuple[object, ...], ...]:
        """Unpack all arguments."""
        args: list[T | tuple[object, ...]] = []
        for arg in self.args:
            if not isinstance(arg, Value):
                args.append(arg)
                continue
            args.append(arg.unpack())
        return tuple(args)

    def unpack_join(self) -> tuple[object | tuple[object, ...], ...]:
        """Unpack all arguments and simplify single argument values."""
        args: list[object | tuple[object, ...]] = []
        for arg in self.args:
            if not isinstance(arg, Value):
                args.append(arg)
                continue
            result = arg.unpack_join()
            if len(result) == 1:
                args.extend(result)
            else:
                args.append(result)
        return tuple(args)


def list_or(values: Collection[str]) -> str:
    """Return comma separated listing of values joined with ` or `."""
    if len(values) <= 2:
        return " or ".join(values)
    copy = list(values)
    copy[-1] = f"or {copy[-1]}"
    return ", ".join(copy)


class Parser:
    """Implementation of the lua parser."""

    __slots__ = ("i", "next_indexed_field", "tokens")

    def __init__(self, tokens: list[Token]) -> None:
        """Initialize with tokens list."""
        self.tokens = tokens
        self.i = 0
        self.next_indexed_field: deque[int] = deque()

    def fail(self, error: str | None) -> NoReturn:
        """Raise parse error."""
        raise ParseError(error)

    def peek(self) -> Token:
        """Peek at next token."""
        if self.i >= len(self.tokens):
            self.fail("Ran out of tokens")
        return self.tokens[self.i]

    def lookup(self) -> str:
        """Peek at next token and return it's text."""
        return self.peek().text
        ##if value is None:
        ##    return "None"

    def next(self) -> Token:
        """Get next token."""
        token = self.peek()
        self.i += 1
        return token

    def back(self) -> None:
        """Go back one token."""
        self.i -= 1

    def rest_tokens(self) -> list[Token]:
        """Return all tokens not processed."""
        return self.tokens[self.i : len(self.tokens)]

    def __repr__(self) -> str:
        """Return representation of self."""
        return f"{self.__class__.__name__}({self.rest_tokens()!r})"

    def expect(self, text: str) -> Token:
        """Expect next token text to be text."""
        token = self.next()
        got = token.text
        if got != text:
            self.fail(f"Expected {text!r}, got {got!r} ({token.location()})")
        return token

    def expect_or(self, options: Collection[str]) -> Token:
        """Expect next token text to be text. Return the token we got."""
        token = self.next()
        if token.text not in options:
            self.fail(
                f"Expected {list_or([repr(x) for x in sorted(options)])}, got {token.text!r} ({token.location()})",
            )
        return token

    def expect_type(
        self,
        token_type: type[Token] | tuple[type[Token], ...],
    ) -> Token:
        """Expect next token to be instance of token_type. Return token."""
        token = self.next()
        if not isinstance(token, token_type):
            if isinstance(token_type, tuple):
                expect_str = list_or(
                    [f"{cls.__name__!r}" for cls in token_type],
                )
            else:
                expect_str = f"{token_type.__name__!r}"
            self.fail(
                f"Expected {expect_str}, got {token!r} ({token.location()})",
            )
        return token

    def parse_string_literal(self) -> Value[str]:
        """Parse a string literal."""
        token = self.expect_type(StrLit)
        # Read the string literal character by character and look for
        # escape sequences like \a, \n, \t, etc.
        value = ""
        skip = 0  # Number of chars to not add to running value
        for idx, char in enumerate(token.text):
            if skip:
                skip -= 1
                continue
            if char != "\\":
                value += char
                continue
            # Is escape sequence start, so read next char to find which one
            value += token.text[idx + 1].translate(
                {
                    97: "\a",
                    98: "\b",
                    102: "\f",
                    110: "\n",
                    114: "\r",
                    116: "\t",
                    118: "\v",
                    92: "\\",
                },
            )
            skip = 1
        return Value("String", value[1:-1], from_token=token)

    def parse_numeric_literal(self) -> Value[int | float]:
        """Parse a numeric literal."""
        token = self.expect_type(Numeric)

        text = token.text
        match_ = HEXADECIMAL.match(text) or NUMERIC.match(text)
        if match_ is None:
            self.fail(
                "Numeric literal regular expression did not match ({token.location()})",
            )
        decimal, fractional, exponent = match_.groups()

        is_float = fractional or exponent

        value: int | float
        if decimal.lower().startswith("0x"):  # is hex?
            value = float.fromhex(text) if is_float else int(text, 16)
            return Value("Float" if is_float else "Integer", value)
        value = float(text) if is_float else int(text)
        return Value("Float" if is_float else "Integer", value, from_token=token)

    def parse_field(self) -> Value[Any]:
        """Parse table field."""
        if self.lookup() == "[":
            start_token = self.expect("[")
            value = self.parse_value()
            self.expect("]")
            self.expect_type(Assignment)
            return Value("Field", value, self.parse_value(), from_token=start_token)
        peek = self.peek()
        if isinstance(peek, Identifier):
            return self.parse_identifier()
        ##        if isinstance(peek, Comment):
        ##            return self.parse_comment()
        index = self.next_indexed_field.pop()
        self.next_indexed_field.append(index + 1)
        # return Value("Indexed", self.parse_value())
        field_value = self.parse_value()
        return Value("Field", Value("Integer", index), field_value, from_token=field_value.from_token)

    def parse_table(self) -> Value[Value[Any]]:
        """Parse table."""
        start_token = self.expect("{")
        self.next_indexed_field.append(1)
        fields: list[Value[object | Value[object]]] = []
        while self.lookup() != "}":
            field = self.parse_field()
            fields.append(field)
            ##            if field.name == "Comment":
            ##                continue

            if self.expect_or({",", ";", "}"}).text == "}":
                self.back()
        self.next_indexed_field.pop()
        self.expect("}")
        return Value("Table", *fields, from_token=start_token)

    def parse_function_arguments(self) -> list[Value[Any]]:
        """Parse function call arguments."""
        self.expect("(")
        arguments = []
        while self.lookup() != ")":
            arguments.append(self.parse_value())

            if self.expect_or({",", ")"}).text == ")":
                self.back()
        self.expect(")")
        return arguments

    def parse_identifier(self) -> Value[Any]:
        """Parse identifier."""
        identifier = self.expect_type(Identifier)
        text = identifier.text
        if text in {"true", "false"}:
            return Value("Boolean", text == "true", from_token=identifier)
        if text in KEYWORDS:
            return Value("Keyword", text, from_token=identifier)
        # Function calls are strange.
        if self.lookup() == "(":  # Regular function call
            return Value(
                "FunctionCall",
                Value("Identifier", text, from_token=identifier),
                Value("Arguments", *self.parse_function_arguments()),
            )
        if self.lookup() == "{":  # syntactic sugar call from table constructor
            return Value(
                "FunctionCall",
                Value("Identifier", text, from_token=identifier),
                Value("Arguments", *self.parse_table()),  # type: ignore[misc]
            )
        if isinstance(
            self.peek(),
            StrLit,
        ):  # syntactic sugar call from string literal
            return Value(
                "FunctionCall",
                Value("Identifier", text, from_token=identifier),
                Value("Arguments", *self.parse_string_literal()),  # type: ignore[misc]
            )
        if isinstance(self.peek(), Assignment):
            self.expect_type(Assignment)
            return Value(
                "Assignment",
                Value("Identifier", text, from_token=identifier),
                self.parse_value(),
            )
        return Value("Identifier", text, from_token=identifier)

    ##    def parse_comment(self) -> Value[str]:
    ##        """Parse Comment."""
    ##        comment = self.expect_type(Comment)
    ##        return Value("Comment", comment.text)

    def parse_value(self) -> Value[Any]:
        """Parse value."""
        peek = self.peek()
        if isinstance(peek, StrLit):
            return self.parse_string_literal()
        if isinstance(peek, Numeric):
            return self.parse_numeric_literal()
        if isinstance(peek, Identifier):
            return self.parse_identifier()
        ##        if isinstance(peek, Comment):
        ##            return self.parse_comment()
        lookup = self.lookup()
        if lookup == "{":
            return self.parse_table()
        raise NotImplementedError(peek)


def parse_lua_table(table_value: Value[Any], convert_lists: bool = True) -> tuple[object, list[Token]]:
    """Parse lua table from lua source."""
    # print(table_value)

    from_tokens: list[Token] = []

    def read_value(value: Value[object]) -> object:
        """Read value base function."""
        assert isinstance(value, Value), value
        if value.name in {
            "String",
            "Boolean",
            "Float",
            "Integer",
            "Identifier",
        }:
            if value.from_token is not None:
                from_tokens.append(value.from_token)
            return value.args[0]
        if value.name == "Table":
            return read_table(cast("Value[Value[object]]", value))
        if value.name == "Assignment":
            return read_assignment(value)
        ##        if value.name == "Comment":
        ##            return read_comment(value)
        if value.name == "Keyword":
            assert isinstance(value.args[0], str)
            return read_keyword(cast("Value[str]", value))
        raise NotImplementedError(f"{value.name} ({value})")

    ##    def read_comment(value: Value[object]) -> str:
    ##        assert value.name == "Comment"
    ##        assert isinstance(value.args[0], str)
    ##        return value.args[0]

    def read_assignment(
        value: Value[Any],
    ) -> tuple[str, object]:
        """Read an Assignment value."""
        assert value.name == "Assignment"
        if value.from_token is not None:
            from_tokens.append(value.from_token)
        key, data = value.args
        return (read_value(key), read_value(data))  # type: ignore[return-value]

    def read_field(
        value: Value[object],
        table: dict[str | int, object],
    ) -> tuple[str | int, object]:
        """Read a table field value."""
        assert value.name in {"Field", "Assignment"}
        if value.name == "Assignment":
            return read_assignment(value)
        # if value.name == "Indexed":
        #    return (str(len(table)), read_value(value.args[0]))
        if value.name == "Field":
            if value.from_token is not None:
                from_tokens.append(value.from_token)
            field, field_value = value.args
            assert isinstance(field, Value)
            assert isinstance(field_value, Value)
            read_field_obj = read_value(field)
            assert isinstance(read_field_obj, str | int)
            return (read_field_obj, read_value(field_value))
        raise NotImplementedError(value.name)

    def read_table(
        value: Value[Value[object]],
    ) -> dict[str | int, object] | list[object]:
        """Read a table and all of it's fields."""
        assert value.name == "Table"
        if value.from_token is not None:
            from_tokens.append(value.from_token)
        table: dict[str | int, object] = {}

        last_int_key = 0
        convert_list = convert_lists

        for field in value.args:
            key, store_value = read_field(field, table)
            if convert_list:
                if not isinstance(key, int):
                    convert_list = False
                elif key == (last_int_key + 1):
                    last_int_key = key
                else:
                    convert_list = False
            table[key] = store_value
        if not convert_list:
            return table
        return [table[i + 1] for i in range(len(table))]

    def read_keyword(value: Value[str]) -> object:
        if value.from_token is not None:
            from_tokens.append(value.from_token)
        if value.args[0] == "nil":
            return None
        raise NotImplementedError(value)

    return read_value(table_value), from_tokens
    # return value.unpack_join()


if __name__ == "__main__":
    print(f"{__title__}\nProgrammed by {__author__}.\n")
