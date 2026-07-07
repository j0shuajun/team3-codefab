from enum import Enum, auto


class TokenType(Enum):
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
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    AND = auto()
    ELSE = auto()
    FALSE = auto()
    FOR = auto()
    IF = auto()
    OR = auto()
    PRINT = auto()
    TRUE = auto()
    VAR = auto()

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


class Tokenizer:
    _SINGLE_CHARACTER_TOKENS = {
        "=": TokenType.EQUAL,
        "(": TokenType.LEFT_PAREN,
        ")": TokenType.RIGHT_PAREN,
        ">": TokenType.GREATER,
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
        return Token(self._SINGLE_CHARACTER_TOKENS[ch], ch)

    def _read_number(self) -> Token:
        characters = self._read_multiple_characters(str.isdigit)
        return Token(TokenType.NUMBER, characters, value=float(characters))

    def _read_identifier(self) -> Token:
        origin = self._read_multiple_characters(str.isalnum)
        if origin == "if":
            return Token(TokenType.IF, origin)
        return Token(TokenType.IDENTIFIER, origin)
