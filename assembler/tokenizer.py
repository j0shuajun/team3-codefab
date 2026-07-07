from enum import Enum, auto
from typing import override


class TokenType(Enum):
    def _generate_next_value_(name, start, count, last_values): # Enum
        # auto() 호출 시 실행되는 함수
        return f"_{name}"

    # 할당
    EQUAL = "="
    # 그룹핑
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    # 블록스코프
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    # 비교
    LESS = "<"
    GREATER = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    EQUAL_EQUAL = "=="
    BANG_EQUAL = "!="
    # 산술연산
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    # 논리연산
    BANG = "!"
    AND = "and"
    OR = "or"
    # 구분자
    SEMICOLON = ";"
    COMMA = ","
    # 변수선언
    VAR = "var"
    # 불리언
    TRUE = "true"
    FALSE = "false"
    # 출력문
    PRINT = "print"
    # 조건문
    IF = "if"
    ELSE = "else"
    # 반복문
    FOR = "for"

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

    _RESERVED_WORDS = frozenset(
        t.value for t in TokenType if isinstance(t.value, str) and t.value.isalpha()
    )

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
        if origin in self._RESERVED_WORDS:
            return Token(TokenType(origin), origin)
        return Token(TokenType.IDENTIFIER, origin)
