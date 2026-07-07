from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from assembler.tokenizer import Token, TokenType


def identifier(name):
    return Token(TokenType.IDENTIFIER, name)


def operator(token_type, origin):
    return Token(token_type, origin)


def test_literal_expr_has_value():
    expr = LiteralExpr(3)

    assert isinstance(expr, Expr)
    assert expr.value == 3


def test_string_literal_expr_has_value():
    expr = LiteralExpr("hello")

    assert isinstance(expr, Expr)
    assert expr.value == "hello"


def test_boolean_literal_expr_has_value():
    expr = LiteralExpr(True)

    assert isinstance(expr, Expr)
    assert expr.value is True


def test_variable_expr_has_name_token():
    name = identifier("a")

    expr = VariableExpr(name)

    assert isinstance(expr, Expr)
    assert expr.name == name
    assert expr.name.type == TokenType.IDENTIFIER
    assert expr.name.origin == "a"


def test_assign_expr_has_name_token_and_value():
    name = identifier("a")
    value = LiteralExpr(10)

    expr = AssignExpr(name, value)

    assert isinstance(expr, Expr)
    assert expr.name == name
    assert expr.name.type == TokenType.IDENTIFIER
    assert expr.name.origin == "a"
    assert expr.value == value


def test_binary_expr_has_left_operator_token_and_right():
    left = LiteralExpr(1)
    plus = operator(TokenType.PLUS, "+")
    right = LiteralExpr(2)

    expr = BinaryExpr(left, plus, right)

    assert isinstance(expr, Expr)
    assert expr.left == left
    assert expr.operator == plus
    assert expr.operator.type == TokenType.PLUS
    assert expr.operator.origin == "+"
    assert expr.right == right


def test_unary_expr_has_operator_token_and_right():
    minus = operator(TokenType.MINUS, "-")
    right = LiteralExpr(3)

    expr = UnaryExpr(minus, right)

    assert isinstance(expr, Expr)
    assert expr.operator == minus
    assert expr.operator.type == TokenType.MINUS
    assert expr.operator.origin == "-"
    assert expr.right == right


def test_grouping_expr_has_expression():
    inner = BinaryExpr(
        LiteralExpr(1),
        operator(TokenType.PLUS, "+"),
        LiteralExpr(2),
    )

    expr = GroupingExpr(inner)

    assert isinstance(expr, Expr)
    assert expr.expression == inner


def test_logical_expr_has_left_operator_token_and_right():
    left = LiteralExpr(True)
    and_token = operator(TokenType.AND, "and")
    right = LiteralExpr(False)

    expr = LogicalExpr(left, and_token, right)

    assert isinstance(expr, Expr)
    assert expr.left == left
    assert expr.operator == and_token
    assert expr.operator.type == TokenType.AND
    assert expr.operator.origin == "and"
    assert expr.right == right


def test_binary_expr_can_represent_operator_precedence_tree():
    # 1 + 2 * 3
    expr = BinaryExpr(
        LiteralExpr(1),
        operator(TokenType.PLUS, "+"),
        BinaryExpr(
            LiteralExpr(2),
            operator(TokenType.STAR, "*"),
            LiteralExpr(3),
        ),
    )

    assert expr.operator.type == TokenType.PLUS
    assert expr.operator.origin == "+"

    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator.type == TokenType.STAR
    assert expr.right.operator.origin == "*"
