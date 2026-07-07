from assembler.assembler import Assembler
from assembler.tokenizer import Token, TokenType
from assembler.expr import LiteralExpr, BinaryExpr, GroupingExpr, UnaryExpr
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

    expression = statements[0].expression

    assert isinstance(expression, BinaryExpr)
    assert expression.operator.type == TokenType.PLUS
    assert expression.left.value == 3
    assert expression.right.value == 2


def test_parse_operator_precedence_tree():
    statements = parse([
        token(TokenType.NUMBER, "3", 3),
        token(TokenType.PLUS, "+"),
        token(TokenType.NUMBER, "7", 7),
        token(TokenType.STAR, "*"),
        token(TokenType.NUMBER, "5", 5),
        token(TokenType.SEMICOLON, ";"),
    ])

    expr = statements[0].expression

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.type == TokenType.PLUS
    assert expr.left.value == 3

    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator.type == TokenType.STAR
    assert expr.right.left.value == 7
    assert expr.right.right.value == 5


def test_parse_grouping_expression():
    statements = parse([
        token(TokenType.LEFT_PAREN, "("),
        token(TokenType.NUMBER, "3", 3),
        token(TokenType.PLUS, "+"),
        token(TokenType.NUMBER, "7", 7),
        token(TokenType.RIGHT_PAREN, ")"),
        token(TokenType.STAR, "*"),
        token(TokenType.NUMBER, "5", 5),
        token(TokenType.SEMICOLON, ";"),
    ])

    expr = statements[0].expression

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.type == TokenType.STAR
    assert isinstance(expr.left, GroupingExpr)


def test_parse_unary_minus_expression():
    statements = parse([
        token(TokenType.MINUS, "-"),
        token(TokenType.NUMBER, "3", 3),
        token(TokenType.SEMICOLON, ";"),
    ])

    expr = statements[0].expression

    assert isinstance(expr, UnaryExpr)
    assert expr.operator.type == TokenType.MINUS
    assert expr.right.value == 3

