from enum import Enum, auto
from typing import override


class TokenType(Enum):
    @override
    def _generate_next_value_(self, start, count, last_values):
        """ auto() 시 호출됨 """
        print(self, start, count, last_values)
        return self

    # 단일문자
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    SEMICOLON = ";"

    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    BANG = "!"
    EQUAL = "="
    GREATER = ">"
    LESS = "<"

    # 여러문자
    VAR = "var"
    TRUE = "true"
    FALSE = "false"
    PRINT = "print"
    AND = "and"
    OR = "or"
    IF = "if"
    ELSE = "else"
    FOR = "for"

    BANG_EQUAL = "!="
    EQUAL_EQUAL = "=="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="

    # 리터럴
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # 기타
    EOF = auto()



class Token:
    def __init__(self, token_type: TokenType, origin: str, value=None):
        self.type = token_type
        self.origin = origin
        if value is not None:
            self.value = value

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return (
            self.type == other.type
            and self.origin == other.origin
            and getattr(self, "value", None) == getattr(other, "value", None)
        )

    def __repr__(self):
        return f"Token({self.type}, {self.origin!r}, {getattr(self, "value", None) !r})"


class Tokenizer:
    _SINGLE_CHARACTERS = frozenset(
        t.value for t in TokenType if isinstance(t.value, str) and len(t.value) == 1
    )

    _CHARACTERS_WITH_EQUAL = frozenset(
        t.value for t in TokenType
        if isinstance(t.value, str) and len(t.value) == 2 and t.value.endswith("=")
    )

    _RESERVED_TOKENS = {
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "var": TokenType.VAR,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "print": TokenType.PRINT,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "for": TokenType.FOR,
    }

    def __init__(self):
        self._origin = ""
        self._idx = 0

    def tokenize(self, string: str) -> list[Token]:
        self._origin = string
        self._idx = 0
        tokens: list[Token] = []

        while self._idx_in_range():
            ch = self._peek()
            if ch.isspace():
                self._idx += 1
            elif ch in self._SINGLE_CHARACTERS:
                tokens.append(self._read_single_character())
            elif ch == '"':
                tokens.append(self._read_string())
            elif ch.isdigit():
                tokens.append(self._read_number())
            elif ch.isalpha():
                tokens.append(self._read_identifier())
            else:
                raise ValueError(f"Unexpected character: {ch!r}")

        tokens.append(Token(TokenType.EOF, ""))
        return tokens

    def _idx_in_range(self) -> bool:
        return self._idx < len(self._origin)

    def _peek(self) -> str:
        return self._origin[self._idx]

    def _read_multiple_characters(self, type_checker) -> str:
        start = self._idx
        while self._idx_in_range() and type_checker(self._peek()):
            self._idx += 1
        return self._origin[start : self._idx]

    def _read_single_character(self) -> Token:
        ch = self._peek()
        self._idx += 1

        if self._idx_in_range():
            combined = ch + self._peek()
            if combined in self._CHARACTERS_WITH_EQUAL:
                self._idx += 1
                return Token(TokenType(combined), combined)

        return Token(TokenType(ch), ch)

    def _read_string(self) -> Token:
        start = self._idx
        self._idx += 1
        while self._idx_in_range() and self._peek() != '"':
            self._idx += 1
        if not self._idx_in_range():
            raise ValueError("Unterminated string")
        self._idx += 1
        origin = self._origin[start : self._idx]
        return Token(TokenType.STRING, origin, value=origin[1:-1])

    def _read_number(self) -> Token:
        characters = self._read_multiple_characters(str.isdigit)
        return Token(TokenType.NUMBER, characters, value=float(characters))

    def _read_identifier(self) -> Token:
        origin = self._read_multiple_characters(str.isalnum)
        return Token(self._RESERVED_TOKENS.get(origin, TokenType.IDENTIFIER), origin)
