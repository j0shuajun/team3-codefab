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
    def __init__(self, type: TokenType, origin: str):
        self.type = type
        self.origin = origin

class Tokenizer:
    def tokenize(self, str: str) -> list[Token]:
        ...