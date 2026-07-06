from assembler.expr import LiteralExpr, BinaryExpr
from assembler.statement import PrintStmt
from assembler.tokenizer import TokenType


class RuntimeError(Exception):
    pass


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

        raise RuntimeError(f"Unknown statement type: {type(stmt).__name__}")

    def evaluate(self, expr):
        if isinstance(expr, LiteralExpr):
            return expr.value

        if isinstance(expr, BinaryExpr):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)

            if expr.operator.type == TokenType.PLUS:
                return left + right

        raise RuntimeError(f"Unknown expression type: {type(expr).__name__}")

    def stringify(self, value):
        return str(value)