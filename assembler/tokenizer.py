from enum import Enum, auto


class TokenType(Enum):
    # End Of File
    EOF = auto()
    # Literal
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    # Assignment
    EQUAL = "="
    # Grouping
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    # Block scope
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    # Array
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    # Member access
    DOT = "."
    # Inheritance
    COLON = ":"
    # Comparison
    LESS = "<"
    GREATER = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    EQUAL_EQUAL = "=="
    BANG_EQUAL = "!="
    # Operation
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    # Logical
    BANG = "!"
    AND = "and"
    OR = "or"
    # Delimiter
    SEMICOLON = ";"
    COMMA = ","
    # Variable
    VAR = "var"
    # Boolean
    TRUE = "true"
    FALSE = "false"
    # Print
    PRINT = "print"
    # Conditional
    IF = "if"
    ELSE = "else"
    # Loop
    FOR = "for"
    # Function
    FUNC = "Func"
    RETURN = "return"
    # Class
    CLASS = "Class"
    THIS = "This"
    SUPER = "Super"
    INSTANCEOF = "instanceof"
    # Import
    IMPORT = "import"
    ALIAS = "alias"


class Token:
    def __init__(self, token_type: TokenType, origin: str, value=None, line: int = 1):
        self.type = token_type
        self.origin = origin
        self.line = line

        if value is not None:
            self.value = value

    def __eq__(self, other):
        # line은 비교하지 않습니다.
        if not isinstance(other, Token):
            return NotImplemented
        return (
            self.type == other.type
            and self.origin == other.origin
            and getattr(self, "value", None) == getattr(other, "value", None)
        )

    def __repr__(self):
        return f"Token({self.type}, {self.origin!r}, {getattr(self, 'value', None)!r}, line={self.line})"


class Tokenizer:
    _TOKENS = {T.value: T for T in TokenType if isinstance(T.value, str)}
    _MAX_TOKEN_LENGTH = max(len(k) for k in _TOKENS)

    def __init__(self):
        self._origin = ""
        self._idx = 0
        self._line = 1

    def tokenize(self, string: str) -> list[Token]:
        self._origin = string
        self._idx = 0
        self._line = 1
        tokens: list[Token] = []

        while self._idx_in_range():
            ch = self._peek()
            if ch == "\n":
                self._line += 1
                self._idx += 1
            elif ch.isspace():
                self._idx += 1
            elif ch == '"':
                tokens.append(self._read_string())
            elif ch.isdigit():
                tokens.append(self._read_number())
            else:
                token = self._read_token()
                if token is not None:
                    tokens.append(token)
                elif ch.isalpha():
                    tokens.append(self._read_generic_identifier())
                else:
                    raise ValueError(f"Unexpected character: {ch!r}")

        tokens.append(Token(TokenType.EOF, "", line=self._line))
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

    def _read_token(self) -> Token | None:
        window = self._origin[self._idx : self._idx + self._MAX_TOKEN_LENGTH]

        for length in range(len(window), 0, -1):
            candidate = window[:length]

            if candidate not in self._TOKENS:
                continue

            if candidate[-1].isalnum():
                next_idx = self._idx + length
                if next_idx < len(self._origin) and self._origin[next_idx].isalnum():
                    continue

            self._idx += length
            return Token(self._TOKENS[candidate], candidate, line=self._line)

        return None

    def _read_string(self) -> Token:
        start = self._idx
        self._idx += 1
        while self._idx_in_range() and self._peek() != '"':
            self._idx += 1
        if not self._idx_in_range():
            raise ValueError("Unterminated string")
        self._idx += 1
        origin = self._origin[start : self._idx]
        if "\\" in origin:
            raise ValueError("Backslash is not allowed")
        return Token(TokenType.STRING, origin, value=origin[1:-1], line=self._line)

    def _read_number(self) -> Token:
        characters = self._read_multiple_characters(str.isdigit)
        if len(characters) > 1 and characters[0] == "0":
            raise ValueError("Number cannot start with zero")
        if self._idx_in_range() and self._peek() == ".":
            characters += self._peek()
            self._idx += 1
            characters += self._read_multiple_characters(str.isdigit)
        return Token(TokenType.NUMBER, characters, float(characters), line=self._line)

    def _read_generic_identifier(self) -> Token:
        origin = self._read_multiple_characters(str.isalnum)
        return Token(TokenType.IDENTIFIER, origin, line=self._line)
