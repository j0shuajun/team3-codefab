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
    def __init__(self, token_type: TokenType, origin: str, value=None, line=1):
        self.type = token_type
        self.origin = origin
        self.line = line

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
        return (
            f"Token("
            f"{self.type}, "
            f"{self.origin!r}, "
            f"{getattr(self, 'value', None)!r}, "
            f"line={self.line}"
            f")"
        )


class Tokenizer:
    _TOKENS = {T.value: T for T in TokenType if isinstance(T.value, str)}

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

            if ch.isspace():
                if ch == "\n":
                    self._line += 1
                self._idx += 1

            elif ch in self._TOKENS:
                tokens.append(self._read_single_character())

            elif ch == '"':
                tokens.append(self._read_string())

            elif ch.isdigit():
                tokens.append(self._read_number())

            elif ch.isalpha():
                tokens.append(self._read_identifier())

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

    def _read_single_character(self) -> Token:
        line = self._line

        ch = self._peek()
        self._idx += 1

        if self._idx_in_range():
            combined = ch + self._peek()
            if combined in self._TOKENS:
                self._idx += 1
                return Token(self._TOKENS[combined], combined, line=line)

        return Token(self._TOKENS[ch], ch, line=line)

    def _read_string(self) -> Token:
        line = self._line

        start = self._idx
        self._idx += 1

        while self._idx_in_range() and self._peek() != '"':
            if self._peek() == "\n":
                self._line += 1
            self._idx += 1

        if not self._idx_in_range():
            raise ValueError("Unterminated string")

        self._idx += 1
        origin = self._origin[start: self._idx]

        return Token(TokenType.STRING, origin, value=origin[1:-1], line=line)

    def _read_number(self) -> Token:
        line = self._line

        characters = self._read_multiple_characters(str.isdigit)

        if len(characters) > 1 and characters[0] == "0":
            raise ValueError("Number cannot start with zero")

        if self._idx_in_range() and self._peek() == ".":
            characters += self._peek()
            self._idx += 1
            characters += self._read_multiple_characters(str.isdigit)

        return Token(TokenType.NUMBER, characters, value=float(characters), line=line)

    def _read_identifier(self) -> Token:
        line = self._line

        origin = self._read_multiple_characters(str.isalnum)

        return Token(
            self._TOKENS.get(origin, TokenType.IDENTIFIER),
            origin,
            line=line,
        )