from assembler.expr import LiteralExpr, BinaryExpr, GroupingExpr, UnaryExpr, VariableExpr, AssignExpr, LogicalExpr
from assembler.statement import PrintStmt, ExpressionStmt, VarStmt, BlockStmt, IfStmt, ForStmt
from assembler.tokenizer import TokenType


class RuntimeError(Exception):
    pass

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name_token):
        name = name_token.origin

        if name in self.values:
            return self.values[name]

        if self.enclosing is not None:
            return self.enclosing.get(name_token)

        raise RuntimeError(f"Undefined variable '{name}'.")

    def assign(self, name_token, value):
        name = name_token.origin

        if name in self.values:
            self.values[name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name_token, value)
            return

        raise RuntimeError(f"Undefined variable '{name}'.")

class Executor:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.outputs = []

    def execute(self, statements):
        for statement in statements:
            self.execute_stmt(statement)

    def execute_stmt(self, stmt):
        if isinstance(stmt, PrintStmt):
            value = self.evaluate(stmt.expression)
            self.outputs.append(self.stringify(value))
            return

        if isinstance(stmt, ExpressionStmt):
            self.evaluate(stmt.expression)
            return

        if isinstance(stmt, VarStmt):
            value = None
            if stmt.initializer is not None:
                value = self.evaluate(stmt.initializer)

            self.environment.define(stmt.name.origin, value)
            return

        if isinstance(stmt, BlockStmt):
            self.execute_block(stmt.statements, Environment(self.environment))
            return

        if isinstance(stmt, IfStmt):
            if self.is_truthy(self.evaluate(stmt.condition)):
                self.execute_stmt(stmt.then_branch)
            elif stmt.else_branch is not None:
                self.execute_stmt(stmt.else_branch)
            return

        if isinstance(stmt, ForStmt):
            self.execute_for(stmt)
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

        if isinstance(expr, VariableExpr):
            return self.environment.get(expr.name)

        if isinstance(expr, AssignExpr):
            value = self.evaluate(expr.value)
            self.environment.assign(expr.name, value)
            return value

        if isinstance(expr, LogicalExpr):
            return self.evaluate_logical(expr)

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

        if expr.operator.type == TokenType.GREATER:
            return left > right

        if expr.operator.type == TokenType.GREATER_EQUAL:
            return left >= right

        if expr.operator.type == TokenType.LESS:
            return left < right

        if expr.operator.type == TokenType.LESS_EQUAL:
            return left <= right

        if expr.operator.type == TokenType.EQUAL_EQUAL:
            return left == right

        if expr.operator.type == TokenType.BANG_EQUAL:
            return left != right

        raise RuntimeError(f"Unknown binary operator: {expr.operator.origin}")

    def stringify(self, value):
        if value is None:
            return "nil"

        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return str(value)

        return str(value)

    def is_truthy(self, value):
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def execute_block(self, statements, environment):
        previous = self.environment

        try:
            self.environment = environment
            for statement in statements:
                self.execute_stmt(statement)
        finally:
            self.environment = previous

    def evaluate_logical(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
            return self.evaluate(expr.right)

        if expr.operator.type == TokenType.AND:
            if not self.is_truthy(left):
                return left
            return self.evaluate(expr.right)

        raise RuntimeError(f"Unknown logical operator: {expr.operator.origin}")

    def execute_for(self, stmt):
        loop_environment = Environment(self.environment)
        previous = self.environment

        try:
            self.environment = loop_environment

            if stmt.initializer is not None:
                self.execute_stmt(stmt.initializer)

            while True:
                if stmt.condition is not None:
                    condition = self.evaluate(stmt.condition)
                    if not self.is_truthy(condition):
                        break

                self.execute_stmt(stmt.body)

                if stmt.increment is not None:
                    self.evaluate(stmt.increment)

        finally:
            self.environment = previous