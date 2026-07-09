import pytest

from app.assembler.assembler import Assembler, AssemblerError
from app.assembler.statement import ImportStmt
from app.assembler.tokenizer import Token, Tokenizer, TokenType


def token(token_type, origin, value=None):
    return Token(token_type, origin, value)


def parse(tokens):
    return Assembler(tokens + [token(TokenType.EOF, "")]).parse()


def parse_source(source):
    return Assembler(Tokenizer().tokenize(source)).parse()


def test_parse_import_statement():
    statements = parse(
        [
            token(TokenType.IMPORT, "import"),
            token(TokenType.STRING, '"sum.txt"', "sum.txt"),
            token(TokenType.ALIAS, "alias"),
            token(TokenType.IDENTIFIER, "sum"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    stmt = statements[0]

    assert isinstance(stmt, ImportStmt)
    assert stmt.path.value == "sum.txt"
    assert stmt.alias.origin == "sum"


def test_import_statement_can_appear_anywhere():
    statements = parse(
        [
            token(TokenType.LEFT_BRACE, "{"),
            token(TokenType.IMPORT, "import"),
            token(TokenType.STRING, '"sum.txt"', "sum.txt"),
            token(TokenType.ALIAS, "alias"),
            token(TokenType.IDENTIFIER, "sum"),
            token(TokenType.SEMICOLON, ";"),
            token(TokenType.RIGHT_BRACE, "}"),
        ]
    )

    block = statements[0]

    assert isinstance(block.statements[0], ImportStmt)


def test_import_requires_string_path():
    with pytest.raises(AssemblerError):
        parse(
            [
                token(TokenType.IMPORT, "import"),
                token(TokenType.IDENTIFIER, "sum"),
                token(TokenType.ALIAS, "alias"),
                token(TokenType.IDENTIFIER, "sum"),
                token(TokenType.SEMICOLON, ";"),
            ]
        )


def test_import_requires_alias_keyword():
    with pytest.raises(AssemblerError):
        parse(
            [
                token(TokenType.IMPORT, "import"),
                token(TokenType.STRING, '"sum.txt"', "sum.txt"),
                token(TokenType.IDENTIFIER, "sum"),
                token(TokenType.SEMICOLON, ";"),
            ]
        )


def test_import_inside_for_loop_body_is_error():
    with pytest.raises(AssemblerError):
        parse_source(
            'for (var i = 0; i < 3; i = i + 1) { import "sum.txt" alias sum; }'
        )


def test_import_inside_nested_block_within_loop_is_error():
    with pytest.raises(AssemblerError):
        parse_source(
            "for (var i = 0; i < 3; i = i + 1) {"
            '  { import "sum.txt" alias sum; }'
            "}"
        )


def test_import_after_loop_is_allowed():
    statements = parse_source(
        "for (var i = 0; i < 3; i = i + 1) { print i; }\n"
        'import "sum.txt" alias sum;\n'
    )

    assert isinstance(statements[1], ImportStmt)


def test_import_outside_loop_is_allowed():
    statements = parse_source('import "sum.txt" alias sum;\n')

    assert isinstance(statements[0], ImportStmt)
