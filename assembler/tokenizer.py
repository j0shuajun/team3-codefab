from enum import auto, Enum


class TokenType(Enum):
    # 단일문자
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    BANG = auto()
    EQUAL = auto()
    GREATER = auto()
    LESS = auto()

    # 여러문자
    VAR = auto()
    TRUE = auto()
    FALSE = auto()
    PRINT = auto()
    AND = auto()
    OR = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()

    BANG_EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()

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
        return (self.type == other.type
                and self.origin == other.origin
                and getattr(self, "value", None) == getattr(other, "value", None))

    def __repr__(self):
        return f"Token({self.type}, {self.origin!r}, {getattr(self, "value", None) !r})"


class Tokenizer:
    _SINGLE_CHARACTER_TOKENS = {
        # 할당
        "=": TokenType.EQUAL,
        # 그룹핑
        "(": TokenType.LEFT_PAREN,
        ")": TokenType.RIGHT_PAREN,
        # 블록스코프
        "{": TokenType.LEFT_BRACE,
        "}": TokenType.RIGHT_BRACE,
        # 비교
        "<": TokenType.LESS,
        ">": TokenType.GREATER,
        # 산술연산
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "/": TokenType.SLASH,
        # 논리연산
        "!": TokenType.BANG,
        # 구분자
        ";": TokenType.SEMICOLON,
        ",": TokenType.COMMA,
    }

    _CHARACTER_WITH_EQUAL_TOKENS = {
        "!": TokenType.BANG_EQUAL,
        "=": TokenType.EQUAL_EQUAL,
        ">": TokenType.GREATER_EQUAL,
        "<": TokenType.LESS_EQUAL,
    }

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
            elif ch in self._SINGLE_CHARACTER_TOKENS:
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
        return self._origin[start:self._idx]

    def _read_single_character(self) -> Token:
        ch = self._peek()
        self._idx += 1

        if ch in self._CHARACTER_WITH_EQUAL_TOKENS and self._idx_in_range() and self._peek() == "=":
            self._idx += 1
            return Token(self._CHARACTER_WITH_EQUAL_TOKENS[ch], ch + "=")

        return Token(self._SINGLE_CHARACTER_TOKENS[ch], ch)

    def _read_string(self) -> Token:
        start = self._idx
        self._idx += 1
        while self._idx_in_range() and self._peek() != '"':
            self._idx += 1
        if not self._idx_in_range():
            raise ValueError("Unterminated string")
        self._idx += 1
        origin = self._origin[start:self._idx]
        return Token(TokenType.STRING, origin, value=origin[1:-1])

    def _read_number(self) -> Token:
        characters = self._read_multiple_characters(str.isdigit)
        return Token(TokenType.NUMBER, characters, value=float(characters))

    def _read_identifier(self) -> Token:
        origin = self._read_multiple_characters(str.isalnum)
        return Token(self._RESERVED_TOKENS.get(origin, TokenType.IDENTIFIER), origin)
