from __future__ import annotations

from assembler.tokenizer import Token


class Expr:
    """Base class for every expression node."""

    pass


class CallExpr(Expr):
    """함수/클래스/native callable 호출 노드"""

    def __init__(self, callee, paren, arguments):
        self.callee = callee  # Expr
        self.paren = paren  # Token: )
        self.arguments = arguments  # list[Expr]

    def __repr__(self):
        return f"CallExpr({self.callee}, args={self.arguments})"


class LiteralExpr(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"LiteralExpr({self.value})"


class VariableExpr(Expr):
    def __init__(self, name: Token):
        self.name = name

    def __repr__(self):
        return f"VariableExpr({self.name.origin})"


class AssignExpr(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"AssignExpr({self.name.origin}, {self.value})"


class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryExpr({self.left}, {self.operator.origin}, {self.right})"


class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"UnaryExpr({self.operator.origin}, {self.right})"


class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self):
        return f"GroupingExpr({self.expression})"


class LogicalExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"LogicalExpr({self.left}, {self.operator.origin}, {self.right})"


class GetExpr(Expr):
    """object.name 필드/메서드 접근"""

    def __init__(self, object_expr: Expr, name: Token):
        self.object = object_expr
        self.name = name

    def __repr__(self):
        return f"GetExpr({self.object}, {self.name.origin})"


class SetExpr(Expr):
    """object.name = value 필드 쓰기"""

    def __init__(self, object_expr: Expr, name: Token, value: Expr):
        self.object = object_expr
        self.name = name
        self.value = value

    def __repr__(self):
        return f"SetExpr({self.object}, {self.name.origin}, {self.value})"


class ThisExpr(Expr):
    """This 표현식"""

    def __init__(self, keyword: Token):
        self.keyword = keyword

    def __repr__(self):
        return "ThisExpr()"
