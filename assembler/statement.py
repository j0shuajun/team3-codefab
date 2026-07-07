class Stmt:
    """Base class for every statement node."""
    pass


class ExpressionStmt(Stmt):
    """expression 하나를 실행하는 문장"""

    def __init__(self, expression):
        self.expression = expression  # Expr

    def __repr__(self):
        return f"ExpressionStmt({self.expression})"


class PrintStmt(Stmt):
    """print expression; 문장"""

    def __init__(self, expression):
        self.expression = expression  # Expr

    def __repr__(self):
        return f"PrintStmt({self.expression})"


class VarStmt(Stmt):
    """var name = initializer; 변수 선언문"""

    def __init__(self, name, initializer=None):
        self.name = name                    # Token
        self.initializer = initializer      # Expr or None

    def __repr__(self):
        return f"VarStmt({self.name.origin}, {self.initializer})"


class BlockStmt(Stmt):
    """{ statement... } 블록 문장"""

    def __init__(self, statements):
        self.statements = statements  # list[Stmt]

    def __repr__(self):
        return f"BlockStmt({self.statements})"


class IfStmt(Stmt):
    """if 조건문"""

    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition          # Expr
        self.then_branch = then_branch      # Stmt
        self.else_branch = else_branch      # Stmt or None

    def __repr__(self):
        return (
            f"IfStmt("
            f"condition={self.condition}, "
            f"then={self.then_branch}, "
            f"else={self.else_branch})"
        )


class ForStmt(Stmt):
    """for 반복문"""

    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer  # Stmt or None
        self.condition = condition      # Expr or None
        self.increment = increment      # Expr or None
        self.body = body                # Stmt

    def __repr__(self):
        return (
            f"ForStmt("
            f"initializer={self.initializer}, "
            f"condition={self.condition}, "
            f"increment={self.increment}, "
            f"body={self.body})"
        )