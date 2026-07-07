from assembler.assembler import Assembler
from assembler.expr import (
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
    VariableExpr, AssignExpr, LogicalExpr,
)
from assembler.statement import ExpressionStmt, PrintStmt, VarStmt, BlockStmt
from assembler.tokenizer import Token, TokenType


def token(token_type, origin, value=None):
    return Token(token_type, origin, value)


def parse(tokens):
    return Assembler(tokens + [token(TokenType.EOF, "")]).parse()


def test_parse_number_expression_statement():
    statements = parse(
        [
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    assert len(statements) == 1
    assert isinstance(statements[0], ExpressionStmt)
    assert isinstance(statements[0].expression, LiteralExpr)
    assert statements[0].expression.value == 3


def test_parse_binary_plus_expression_tree():
    statements = parse(
        [
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.PLUS, "+"),
            token(TokenType.NUMBER, "2", 2),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expression = statements[0].expression

    assert isinstance(expression, BinaryExpr)
    assert expression.operator.type == TokenType.PLUS
    assert expression.left.value == 3
    assert expression.right.value == 2


def test_parse_operator_precedence_tree():
    statements = parse(
        [
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.PLUS, "+"),
            token(TokenType.NUMBER, "7", 7),
            token(TokenType.STAR, "*"),
            token(TokenType.NUMBER, "5", 5),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.type == TokenType.PLUS
    assert expr.left.value == 3

    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator.type == TokenType.STAR
    assert expr.right.left.value == 7
    assert expr.right.right.value == 5


def test_parse_grouping_expression():
    statements = parse(
        [
            token(TokenType.LEFT_PAREN, "("),
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.PLUS, "+"),
            token(TokenType.NUMBER, "7", 7),
            token(TokenType.RIGHT_PAREN, ")"),
            token(TokenType.STAR, "*"),
            token(TokenType.NUMBER, "5", 5),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.type == TokenType.STAR
    assert isinstance(expr.left, GroupingExpr)


def test_parse_unary_minus_expression():
    statements = parse(
        [
            token(TokenType.MINUS, "-"),
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, UnaryExpr)
    assert expr.operator.type == TokenType.MINUS
    assert expr.right.value == 3


def test_parse_string():
    statements = parse(
        [
            token(TokenType.STRING, "hello", "hello"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    assert statements[0].expression.value == "hello"


def test_parse_boolean():
    statements = parse(
        [
            token(TokenType.TRUE, "true"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    assert statements[0].expression.value is True


def test_parse_variable():
    statements = parse(
        [
            token(TokenType.IDENTIFIER, "a"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    assert isinstance(statements[0].expression, VariableExpr)
    assert statements[0].expression.name.origin == "a"


def test_parse_print_statement():
    statements = parse(
        [
            token(TokenType.PRINT, "print"),
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    assert isinstance(statements[0], PrintStmt)
    assert statements[0].expression.value == 3


def test_parse_var_declaration_empty():
    statements = parse(
        [
            token(TokenType.VAR, "var"),
            token(TokenType.IDENTIFIER, "a"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    stmt = statements[0]

    assert isinstance(stmt, VarStmt)
    assert stmt.name.origin == "a"


def test_parse_var_declaration():
    statements = parse(
        [
            token(TokenType.VAR, "var"),
            token(TokenType.IDENTIFIER, "a"),
            token(TokenType.EQUAL, "="),
            token(TokenType.NUMBER, "10", 10),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    stmt = statements[0]

    assert isinstance(stmt, VarStmt)
    assert stmt.name.origin == "a"
    assert stmt.initializer.value == 10


def test_parse_assignment_expression():
    statements = parse([
        token(TokenType.IDENTIFIER, "a"),
        token(TokenType.EQUAL, "="),
        token(TokenType.NUMBER, "20", 20),
        token(TokenType.SEMICOLON, ";"),
    ])

    expr = statements[0].expression

    assert isinstance(expr, AssignExpr)
    assert expr.name.origin == "a"
    assert expr.value.value == 20


def test_parse_comparison_and_equality_expression():
    statements = parse([
        token(TokenType.IDENTIFIER, "a"),
        token(TokenType.GREATER, ">"),
        token(TokenType.NUMBER, "3", 3),
        token(TokenType.EQUAL_EQUAL, "=="),
        token(TokenType.TRUE, "true"),
        token(TokenType.SEMICOLON, ";"),
    ])

    expr = statements[0].expression

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.type == TokenType.EQUAL_EQUAL
    assert isinstance(expr.left, BinaryExpr)
    assert expr.left.operator.type == TokenType.GREATER


def test_parse_logical_expression():
    statements = parse([
        token(TokenType.TRUE, "true"),
        token(TokenType.AND, "and"),
        token(TokenType.FALSE, "false"),
        token(TokenType.OR, "or"),
        token(TokenType.TRUE, "true"),
        token(TokenType.SEMICOLON, ";"),
    ])

    expr = statements[0].expression

    assert isinstance(expr, LogicalExpr)
    assert expr.operator.type == TokenType.OR
    assert isinstance(expr.left, LogicalExpr)
    assert expr.left.operator.type == TokenType.AND


def test_parse_block_statement():
    statements = parse([
        token(TokenType.LEFT_BRACE, "{"),
        token(TokenType.VAR, "var"),
        token(TokenType.IDENTIFIER, "a"),
        token(TokenType.EQUAL, "="),
        token(TokenType.NUMBER, "1", 1),
        token(TokenType.SEMICOLON, ";"),
        token(TokenType.PRINT, "print"),
        token(TokenType.IDENTIFIER, "a"),
        token(TokenType.SEMICOLON, ";"),
        token(TokenType.RIGHT_BRACE, "}"),
    ])

    stmt = statements[0]

    assert isinstance(stmt, BlockStmt)
    assert len(stmt.statements) == 2
    assert isinstance(stmt.statements[0], VarStmt)
    assert isinstance(stmt.statements[1], PrintStmt)

