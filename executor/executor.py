from assembler.environment import CodeFabRuntimeError, Environment
from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from assembler.runtime import Callable, NativeFunction, ReturnSignal, UserFunction
from assembler.statement import (
    BlockStmt,
    ExpressionStmt,
    ForStmt,
    FunctionStmt,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    VarStmt,
)
from assembler.tokenizer import TokenType
from exceptions import CodeFabRuntimeError


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

        raise CodeFabRuntimeError(f"Undefined variable '{name}'.")

    def assign(self, name_token, value):
        name = name_token.origin

        if name in self.values:
            self.values[name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name_token, value)
            return

        raise CodeFabRuntimeError(f"Undefined variable '{name}'.")

    def ancestor(self, distance):
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def get_at(self, distance, name):
        return self.ancestor(distance).values[name]

    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name] = value




class Executor:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.outputs = []

        self.globals.define("add", NativeFunction("add", 2, lambda a, b: a + b))

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

        if isinstance(stmt, FunctionStmt):
            function = UserFunction(stmt, self.environment)
            self.environment.define(stmt.name.origin, function)
            return

        if isinstance(stmt, ReturnStmt):
            value = None
            if stmt.value is not None:
                value = self.evaluate(stmt.value)
            raise ReturnSignal(value)

        raise CodeFabRuntimeError(f"Unknown statement type: {type(stmt).__name__}")

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
                self.check_number_operand(right)
                return -right

            if expr.operator.type == TokenType.BANG:
                return not self.is_truthy(right)

            raise CodeFabRuntimeError(f"Unknown unary operator: {expr.operator.origin}")

        if isinstance(expr, VariableExpr):
            distance = getattr(expr, "distance", None)
            if distance is not None:
                return self.environment.get_at(distance, expr.name.origin)
            return self.environment.get(expr.name)

        if isinstance(expr, AssignExpr):
            value = self.evaluate(expr.value)
            distance = getattr(expr, "distance", None)
            if distance is not None:
                self.environment.assign_at(distance, expr.name.origin, value)
            else:
                self.environment.assign(expr.name, value)
            return value

        if isinstance(expr, LogicalExpr):
            return self.evaluate_logical(expr)
        if isinstance(expr, CallExpr):
            return self.evaluate_call(expr)

        raise CodeFabRuntimeError(f"Unknown expression type: {type(expr).__name__}")

    def evaluate_binary(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.type == TokenType.PLUS:
            if self.is_number(left) and self.is_number(right):
                return left + right

            if isinstance(left, str) and isinstance(right, str):
                return left + right

            raise CodeFabRuntimeError("Operands must be two numbers or two strings.")

        if expr.operator.type == TokenType.MINUS:
            self.check_number_operands(left, right)
            return left - right

        if expr.operator.type == TokenType.STAR:
            self.check_number_operands(left, right)
            return left * right

        if expr.operator.type == TokenType.SLASH:
            self.check_number_operands(left, right)
            if right == 0:
                raise CodeFabRuntimeError("Division by zero.")
            return left / right

        if expr.operator.type == TokenType.GREATER:
            self.check_type_different(left, right)
            return left > right

        if expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_type_different(left, right)
            return left >= right

        if expr.operator.type == TokenType.LESS:
            self.check_type_different(left, right)
            return left < right

        if expr.operator.type == TokenType.LESS_EQUAL:
            self.check_type_different(left, right)
            return left <= right

        if expr.operator.type == TokenType.EQUAL_EQUAL:
            self.check_type_different(left, right)
            return left == right

        if expr.operator.type == TokenType.BANG_EQUAL:
            return left != right

        raise CodeFabRuntimeError(f"Unknown binary operator: {expr.operator.origin}")

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

        raise CodeFabRuntimeError(f"Unknown logical operator: {expr.operator.origin}")

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

    def is_number(self, value):
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def check_number_operand(self, operand):
        if self.is_number(operand):
            return

        raise CodeFabRuntimeError("Operand must be a number.")

    def check_number_operands(self, left, right):
        if self.is_number(left) and self.is_number(right):
            return

        raise CodeFabRuntimeError("Operands must be numbers.")

    def check_type_different(self, left, right):
        if self.is_number(left) or self.is_number(right):
            if self.is_number(left) and self.is_number(right):
                return
            raise CodeFabRuntimeError("Left/Right type mismatch.")

        if left.type == right.type:
            return
        raise CodeFabRuntimeError("Left/Right type mismatch.")

    def evaluate_call(self, expr):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, Callable):
            raise CodeFabRuntimeError("Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise CodeFabRuntimeError(
                f"Expected {callee.arity()} arguments but got {len(arguments)}."
            )

        return callee.call(self, arguments)
