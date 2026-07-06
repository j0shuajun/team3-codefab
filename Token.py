class TokenType(Enum):
    IF = auto()
    FOR = auto()
    VAR = auto()

class Token:
    def __init__(self, type: TokenType, origin: str):
        self.type = type
        self.origin = origin

class Tokenizer:
    def tokenize(self, str: str) -> list[Token]:
        ...