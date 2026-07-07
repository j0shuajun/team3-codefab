from assembler.assembler import Assembler
from assembler.tokenizer import Token, TokenType
from assembler.expr import LiteralExpr, BinaryExpr
from assembler.statement import ExpressionStmt


def token(token_type, origin, value=None):
    return Token(token_type, origin, value)


def parse(tokens):
    return Assembler(tokens + [token(TokenType.EOF, "")]).parse()


def test_parse_number_expression_statement():
    statements = parse([
        token(TokenType.NUMBER, "3", 3),
        token(TokenType.SEMICOLON, ";"),
    ])

    assert len(statements) == 1
    assert isinstance(statements[0], ExpressionStmt)
    assert isinstance(statements[0].expression, LiteralExpr)
    assert statements[0].expression.value == 3


def test_parse_binary_plus_expression_tree():
    statements = parse([
        token(TokenType.NUMBER, "3", 3),
        token(TokenType.PLUS, "+"),
        token(TokenType.NUMBER, "2", 2),
        token(TokenType.SEMICOLON, ";"),
    ])

    expr = statements[0].expression

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.type == TokenType.PLUS
    assert expr.left.value == 3
    assert expr.right.value == 2


