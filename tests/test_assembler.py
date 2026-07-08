from assembler.assembler import Assembler
from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    GroupingExpr,
    IndexGetExpr,
    IndexSetExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from assembler.statement import (
    BlockStmt,
    ExpressionStmt,
    ForStmt,
    IfStmt,
    PrintStmt,
    VarStmt,
)
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
    statements = parse(
        [
            token(TokenType.IDENTIFIER, "a"),
            token(TokenType.EQUAL, "="),
            token(TokenType.NUMBER, "20", 20),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, AssignExpr)
    assert expr.name.origin == "a"
    assert expr.value.value == 20


def test_parse_comparison_and_equality_expression():
    statements = parse(
        [
            token(TokenType.IDENTIFIER, "a"),
            token(TokenType.GREATER, ">"),
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.EQUAL_EQUAL, "=="),
            token(TokenType.TRUE, "true"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.type == TokenType.EQUAL_EQUAL
    assert isinstance(expr.left, BinaryExpr)
    assert expr.left.operator.type == TokenType.GREATER


def test_parse_logical_expression():
    statements = parse(
        [
            token(TokenType.TRUE, "true"),
            token(TokenType.AND, "and"),
            token(TokenType.FALSE, "false"),
            token(TokenType.OR, "or"),
            token(TokenType.TRUE, "true"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, LogicalExpr)
    assert expr.operator.type == TokenType.OR
    assert isinstance(expr.left, LogicalExpr)
    assert expr.left.operator.type == TokenType.AND


def test_parse_block_statement():
    statements = parse(
        [
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
        ]
    )

    stmt = statements[0]

    assert isinstance(stmt, BlockStmt)
    assert len(stmt.statements) == 2
    assert isinstance(stmt.statements[0], VarStmt)
    assert isinstance(stmt.statements[1], PrintStmt)


def test_parse_if_else_statement():
    statements = parse(
        [
            token(TokenType.IF, "if"),
            token(TokenType.LEFT_PAREN, "("),
            token(TokenType.IDENTIFIER, "a"),
            token(TokenType.GREATER, ">"),
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.RIGHT_PAREN, ")"),
            token(TokenType.PRINT, "print"),
            token(TokenType.NUMBER, "1", 1),
            token(TokenType.SEMICOLON, ";"),
            token(TokenType.ELSE, "else"),
            token(TokenType.PRINT, "print"),
            token(TokenType.NUMBER, "2", 2),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    stmt = statements[0]

    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert isinstance(stmt.then_branch, PrintStmt)
    assert isinstance(stmt.else_branch, PrintStmt)


def test_parse_for_statement():
    statements = parse(
        [
            token(TokenType.FOR, "for"),
            token(TokenType.LEFT_PAREN, "("),
            token(TokenType.VAR, "var"),
            token(TokenType.IDENTIFIER, "i"),
            token(TokenType.EQUAL, "="),
            token(TokenType.NUMBER, "0", 0),
            token(TokenType.SEMICOLON, ";"),
            token(TokenType.IDENTIFIER, "i"),
            token(TokenType.LESS, "<"),
            token(TokenType.NUMBER, "3", 3),
            token(TokenType.SEMICOLON, ";"),
            token(TokenType.IDENTIFIER, "i"),
            token(TokenType.EQUAL, "="),
            token(TokenType.IDENTIFIER, "i"),
            token(TokenType.PLUS, "+"),
            token(TokenType.NUMBER, "1", 1),
            token(TokenType.RIGHT_PAREN, ")"),
            token(TokenType.PRINT, "print"),
            token(TokenType.IDENTIFIER, "i"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    stmt = statements[0]

    assert isinstance(stmt, ForStmt)
    assert isinstance(stmt.initializer, VarStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert isinstance(stmt.increment, AssignExpr)
    assert isinstance(stmt.body, PrintStmt)


def test_parse_call_expression():
    statements = parse(
        [
            token(TokenType.IDENTIFIER, "add"),
            token(TokenType.LEFT_PAREN, "("),
            token(TokenType.NUMBER, "1", 1),
            token(TokenType.COMMA, ","),
            token(TokenType.NUMBER, "2", 2),
            token(TokenType.RIGHT_PAREN, ")"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, CallExpr)
    assert isinstance(expr.callee, VariableExpr)
    assert expr.callee.name.origin == "add"
    assert len(expr.arguments) == 2
    assert expr.arguments[0].value == 1
    assert expr.arguments[1].value == 2


def test_parse_index_get_expression():
    statements = parse(
        [
            token(TokenType.IDENTIFIER, "arr"),
            token(TokenType.LEFT_BRACKET, "["),
            token(TokenType.NUMBER, "0", 0),
            token(TokenType.RIGHT_BRACKET, "]"),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, IndexGetExpr)
    assert isinstance(expr.array, VariableExpr)
    assert expr.array.name.origin == "arr"
    assert expr.index.value == 0


def test_parse_index_set_expression():
    statements = parse(
        [
            token(TokenType.IDENTIFIER, "arr"),
            token(TokenType.LEFT_BRACKET, "["),
            token(TokenType.NUMBER, "0", 0),
            token(TokenType.RIGHT_BRACKET, "]"),
            token(TokenType.EQUAL, "="),
            token(TokenType.NUMBER, "7", 7),
            token(TokenType.SEMICOLON, ";"),
        ]
    )

    expr = statements[0].expression

    assert isinstance(expr, IndexSetExpr)
    assert isinstance(expr.array, VariableExpr)
    assert expr.array.name.origin == "arr"
    assert expr.index.value == 0
    assert expr.value.value == 7
