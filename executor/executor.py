from assembler.expr import LiteralExpr, BinaryExpr, GroupingExpr, UnaryExpr
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
            return self.evaluate_binary(expr)

        if isinstance(expr, GroupingExpr):
            return self.evaluate(expr.expression)

        if isinstance(expr, UnaryExpr):
            right = self.evaluate(expr.right)

            if expr.operator.type == TokenType.MINUS:
                return -right

            if expr.operator.type == TokenType.BANG:
                return not self.is_truthy(right)

            raise RuntimeError(f"Unknown unary operator: {expr.operator.origin}")

        raise RuntimeError(f"Unknown expression type: {type(expr).__name__}")

    def evaluate_binary(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.PLUS:
            return left + right

        if expr.operator.type == TokenType.MINUS:
            return left - right

        if expr.operator.type == TokenType.STAR:
            return left * right

        if expr.operator.type == TokenType.SLASH:
            return left / right

        raise RuntimeError(f"Unknown binary operator: {expr.operator.origin}")

    def stringify(self, value):
        return str(value)

    def is_truthy(self, value):
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True