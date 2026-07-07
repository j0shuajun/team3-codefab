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


def test_literal_expr_has_value():
    expr = LiteralExpr(3)

    assert isinstance(expr, Expr)
    assert expr.value == 3


def test_string_literal_expr_has_value():
    expr = LiteralExpr("hello")

    assert expr.value == "hello"


def test_boolean_literal_expr_has_value():
    expr = LiteralExpr(True)

    assert expr.value is True


def test_variable_expr_has_name_token():
    name = Token(TokenType.IDENTIFIER, "a")

    expr = VariableExpr(name)

    assert isinstance(expr, Expr)
    assert expr.name == name
    assert expr.name.type == TokenType.IDENTIFIER
    assert expr.name.origin == "a"


def test_assign_expr_has_name_and_value():
    name = Token(TokenType.IDENTIFIER, "a")
    value = LiteralExpr(10)

    expr = AssignExpr(name, value)

    assert isinstance(expr, Expr)
    assert expr.name == name
    assert expr.value == value


def test_binary_expr_has_left_operator_right():
    left = LiteralExpr(1)
    operator = Token(TokenType.PLUS, "+")
    right = LiteralExpr(2)

    expr = BinaryExpr(left, operator, right)

    assert isinstance(expr, Expr)
    assert expr.left == left
    assert expr.operator == operator
    assert expr.right == right


def test_unary_expr_has_operator_and_right():
    operator = Token(TokenType.MINUS, "-")
    right = LiteralExpr(3)

    expr = UnaryExpr(operator, right)

    assert isinstance(expr, Expr)
    assert expr.operator == operator
    assert expr.right == right


def test_grouping_expr_has_expression():
    inner = BinaryExpr(
        LiteralExpr(1),
        Token(TokenType.PLUS, "+"),
        LiteralExpr(2),
    )

    expr = GroupingExpr(inner)

    assert isinstance(expr, Expr)
    assert expr.expression == inner


def test_logical_expr_has_left_operator_right():
    left = LiteralExpr(True)
    operator = Token(TokenType.AND, "and")
    right = LiteralExpr(False)

    expr = LogicalExpr(left, operator, right)

    assert isinstance(expr, Expr)
    assert expr.left == left
    assert expr.operator == operator
    assert expr.right == right


def test_binary_expr_can_represent_operator_precedence_tree():
    # 1 + 2 * 3
    expr = BinaryExpr(
        LiteralExpr(1),
        Token(TokenType.PLUS, "+"),
        BinaryExpr(
            LiteralExpr(2),
            Token(TokenType.STAR, "*"),
            LiteralExpr(3),
        ),
    )

    assert expr.operator.type == TokenType.PLUS
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator.type == TokenType.STAR
