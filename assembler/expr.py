class Expr:
    """Base class for every expression node."""

    pass


class LiteralExpr(Expr):
    """숫자, 문자열, true, false 같은 값 자체를 나타내는 노드"""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"LiteralExpr({self.value})"


class VariableExpr(Expr):
    """변수 이름을 참조하는 노드"""

    def __init__(self, name):
        self.name = name  # Token

    def __repr__(self):
        return f"VariableExpr({self.name.origin})"


class AssignExpr(Expr):
    """변수에 값을 대입하는 노드"""

    def __init__(self, name, value):
        self.name = name  # Token
        self.value = value  # Expr

    def __repr__(self):
        return f"AssignExpr({self.name.origin}, {self.value})"


class BinaryExpr(Expr):
    """left operator right 형태의 이항 연산 노드"""

    def __init__(self, left, operator, right):
        self.left = left  # Expr
        self.operator = operator  # Token
        self.right = right  # Expr

    def __repr__(self):
        return f"BinaryExpr({self.left}, {self.operator.origin}, {self.right})"


class UnaryExpr(Expr):
    """operator right 형태의 단항 연산 노드"""

    def __init__(self, operator, right):
        self.operator = operator  # Token
        self.right = right  # Expr

    def __repr__(self):
        return f"UnaryExpr({self.operator.origin}, {self.right})"


class GroupingExpr(Expr):
    """괄호로 묶인 expression 노드"""

    def __init__(self, expression):
        self.expression = expression  # Expr

    def __repr__(self):
        return f"GroupingExpr({self.expression})"


class LogicalExpr(Expr):
    """and / or 논리 연산 노드"""

    def __init__(self, left, operator, right):
        self.left = left  # Expr
        self.operator = operator  # Token
        self.right = right  # Expr

    def __repr__(self):
        return f"LogicalExpr({self.left}, {self.operator.origin}, {self.right})"
