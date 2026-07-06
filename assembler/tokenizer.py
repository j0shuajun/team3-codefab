from enum import auto, Enum

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
        return (self.type == other.type
                and self.origin == other.origin
                and getattr(self, "value", None) == getattr(other, "value", None))

class Tokenizer:
    def __init__(self):
        pass

    def tokenize(self, string: str) -> list[Token]:
        tokens = []
        i = 0
        n = len(string)
        while i < n:
            c = string[i]
            if c.isspace():
                i += 1
                continue
            if c == "=":
                tokens.append(Token(TokenType.EQUAL, "="))
                i += 1
                continue
            if c.isdigit():
                start = i
                while i < n and string[i].isdigit():
                    i += 1
                origin = string[start:i]
                tokens.append(Token(TokenType.NUMBER, origin, value=float(origin)))
                continue
            if c.isalpha():
                start = i
                while i < n and string[i].isalnum():
                    i += 1
                origin = string[start:i]
                tokens.append(Token(TokenType.IDENTIFIER, origin))
                continue
            raise ValueError(f"Unexpected character: {c!r}")

        tokens.append(Token(TokenType.EOF, ""))
        return tokens

