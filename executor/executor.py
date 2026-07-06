from assembler.expr import LiteralExpr
from assembler.statement import PrintStmt


class Executor:
    def __init__(self):
        self.outputs = []

    def execute(self, statements):
        for statement in statements:
            self.execute_stmt(statement)

    def execute_stmt(self, stmt):
        if isinstance(stmt, PrintStmt):
            value = self.evaluate(stmt.expression)
            self.outputs.append(self.stringify(value))
            return

        raise Exception(f"Unknown statement type: {type(stmt).__name__}")

    def evaluate(self, expr):
        if isinstance(expr, LiteralExpr):
            return expr.value

        raise Exception(f"Unknown expression type: {type(expr).__name__}")

    def stringify(self, value):
        return str(value)