from __future__ import annotations

from assembler.tokenizer import Token


class Expr:
    """Base class for every expression node."""

    pass


class LiteralExpr(Expr):
    def __init__(self, value):
        self.value = value


class VariableExpr(Expr):
    def __init__(self, name: Token):
        self.name = name


class AssignExpr(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value


class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right


class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression


class LogicalExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right
