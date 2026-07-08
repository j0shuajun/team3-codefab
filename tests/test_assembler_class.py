from assembler.assembler import Assembler
from assembler.expr import GetExpr, SetExpr, ThisExpr, CallExpr, SuperExpr
from assembler.statement import ClassStmt, FunctionStmt
from assembler.tokenizer import Token, TokenType


def token(token_type, origin, value=None):
    return Token(token_type, origin, value)


def parse(tokens):
    return Assembler(tokens + [token(TokenType.EOF, "")]).parse()


def test_parse_get_expression():
    statements = parse(
        [
            token(TokenType.IDENTIFIER, "r"),
            token(TokenType.DOT, "."),
            token(TokenType.IDENTIFIER, "name"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, GetExpr)
    assert expr.name.origin == "name"


def test_parse_set_expression():
    statements = parse(
        [
            token(TokenType.IDENTIFIER, "r"),
            token(TokenType.DOT, "."),
            token(TokenType.IDENTIFIER, "name"),
            token(TokenType.EQUAL, "="),
            token(TokenType.STRING, "Robot", "Robot"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, SetExpr)
    assert expr.name.origin == "name"
    assert expr.value.value == "Robot"


def test_parse_this_expression():
    statements = parse(
        [
            token(TokenType.THIS, "This"),
            token(TokenType.DOT, "."),
            token(TokenType.IDENTIFIER, "name"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, GetExpr)
    assert isinstance(expr.object, ThisExpr)


def test_parse_class_declaration_with_method():
    statements = parse(
        [
            token(TokenType.CLASS, "Class"),
            token(TokenType.IDENTIFIER, "Robot"),
            token(TokenType.LEFT_BRACE, "{"),
            token(TokenType.IDENTIFIER, "report"),
            token(TokenType.LEFT_PAREN, "("),
            token(TokenType.RIGHT_PAREN, ")"),
            token(TokenType.LEFT_BRACE, "{"),
            token(TokenType.RIGHT_BRACE, "}"),
            token(TokenType.RIGHT_BRACE, "}"),
        ]
    )

    stmt = statements[0]

    assert isinstance(stmt, ClassStmt)
    assert stmt.name.origin == "Robot"
    assert len(stmt.methods) == 1
    assert isinstance(stmt.methods[0], FunctionStmt)
    assert stmt.methods[0].name.origin == "report"


def test_parse_class_declaration_with_superclass():
    statements = parse([
        token(TokenType.CLASS, "Class"),
        token(TokenType.IDENTIFIER, "SpeedRobot"),
        token(TokenType.COLON, ":"),
        token(TokenType.IDENTIFIER, "Robot"),
        token(TokenType.LEFT_BRACE, "{"),
        token(TokenType.RIGHT_BRACE, "}"),
    ])

    stmt = statements[0]

    assert isinstance(stmt, ClassStmt)
    assert stmt.name.origin == "SpeedRobot"
    assert stmt.superclass.name.origin == "Robot"
    assert stmt.methods == []


def test_parse_super_method_expression():
    statements = parse([
        token(TokenType.SUPER, "Super"),
        token(TokenType.DOT, "."),
        token(TokenType.IDENTIFIER, "move"),
        token(TokenType.LEFT_PAREN, "("),
        token(TokenType.RIGHT_PAREN, ")"),
        token(TokenType.SEMICOLON, ";"),
    ])

    expr = statements[0].expression

    assert isinstance(expr, CallExpr)
    assert isinstance(expr.callee, SuperExpr)
    assert expr.callee.method.origin == "move"
