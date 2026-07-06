class Expr:
    """Base class for every expression node."""

    pass


class LiteralExpr(Expr):
    def __init__(self, value):
        self.value = value


class VariableExpr(Expr):
    def __init__(self, name):
        self.name = name


class AssignExpr(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class BinaryExpr(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryExpr(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right


class GroupingExpr(Expr):
    def __init__(self, expression):
        self.expression = expression


class LogicalExpr(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
