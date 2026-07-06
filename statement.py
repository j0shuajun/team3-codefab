class Stmt:
    """Base class for every statement node."""

    pass


class ExpressionStmt(Stmt):
    def __init__(self, expression):
        self.expression = expression


class PrintStmt(Stmt):
    def __init__(self, expression):
        self.expression = expression


class VarStmt(Stmt):
    def __init__(self, name, initializer=None):
        self.name = name
        self.initializer = initializer


class BlockStmt(Stmt):
    def __init__(self, statements):
        self.statements = statements


class IfStmt(Stmt):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class ForStmt(Stmt):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body
