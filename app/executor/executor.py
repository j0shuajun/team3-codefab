from app.assembler.environment import Environment
from app.assembler.expr import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    GetExpr,
    GroupingExpr,
    IndexGetExpr,
    IndexSetExpr,
    LiteralExpr,
    LogicalExpr,
    SetExpr,
    SuperExpr,
    ThisExpr,
    UnaryExpr,
    VariableExpr,
)
from app.assembler.runtime import (
    Callable,
    NativeFunction,
    ReturnSignal,
    UserClass,
    UserFunction,
    UserInstance,
)
from app.assembler.statement import (
    BlockStmt,
    ClassStmt,
    ExpressionStmt,
    ForStmt,
    FunctionStmt,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    VarStmt,
)
from app.assembler.tokenizer import TokenType
from app.exceptions import CodeFabRuntimeError


class Executor:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.outputs = []

        self.globals.define("add", NativeFunction("add", 2, lambda a, b: a + b))
        self.globals.define("Array", NativeFunction("Array", 1, self._make_array))

    def _make_array(self, size):
        if not self.is_number(size):
            raise CodeFabRuntimeError("Array size must be a number.")
        if not float(size).is_integer():
            raise CodeFabRuntimeError("Array size must be an integer.")
        if size < 0:
            raise CodeFabRuntimeError("Array size must not be negative.")
        return [None] * int(size)

    def execute(self, statements):
        for statement in statements:
            self.execute_stmt(statement)

    def execute_stmt(self, stmt):
        try:
            self._execute_stmt(stmt)
        except CodeFabRuntimeError as error:
            if getattr(error, "line", None) is None:
                error.line = getattr(stmt, "line", None)
            raise

    def _execute_stmt(self, stmt):
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

        if isinstance(stmt, ClassStmt):
            superclass = None

            if stmt.superclass is not None:
                superclass = self.evaluate(stmt.superclass)

                if not isinstance(superclass, UserClass):
                    raise CodeFabRuntimeError("Superclass must be a class.")

            self.environment.define(stmt.name.origin, None)

            if superclass is not None:
                self.environment = Environment(self.environment)
                self.environment.define("Super", superclass)

            methods = {}
            for method in stmt.methods:
                function = UserFunction(method, self.environment)
                methods[method.name.origin] = function

            klass = UserClass(stmt.name.origin, methods, superclass)

            if superclass is not None:
                self.environment = self.environment.enclosing

            self.environment.assign(stmt.name, klass)
            return

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
        if isinstance(expr, IndexGetExpr):
            return self.evaluate_index_get(expr)
        if isinstance(expr, IndexSetExpr):
            return self.evaluate_index_set(expr)

        if isinstance(expr, GetExpr):
            obj = self.evaluate(expr.object)

            if isinstance(obj, UserInstance):
                return obj.get(expr.name)

            raise CodeFabRuntimeError("Only instances have properties.")

        if isinstance(expr, SetExpr):
            obj = self.evaluate(expr.object)

            if not isinstance(obj, UserInstance):
                raise CodeFabRuntimeError("Only instances have fields.")

            value = self.evaluate(expr.value)
            obj.set(expr.name, value)
            return value

        if isinstance(expr, ThisExpr):
            return self.environment.get(expr.keyword)

        if isinstance(expr, SuperExpr):
            superclass = self.environment.get(expr.keyword)

            this_token = type("TokenLike", (), {"origin": "This"})()

            instance = self.environment.get(this_token)

            method = superclass.find_method(expr.method.origin)

            if method is None:
                raise CodeFabRuntimeError(f"Undefined property '{expr.method.origin}'.")

            return method.bind(instance)

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

        if expr.operator.type == TokenType.INSTANCEOF:
            if not isinstance(left, UserInstance):
                return False

            if not isinstance(right, UserClass):
                raise CodeFabRuntimeError(
                    "Right operand of instanceof must be a class."
                )

            return left.is_instance_of(right)

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

        if type(left) is type(right):
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

    def evaluate_index_get(self, expr):
        array, index = self.resolve_index(expr)
        return array[index]

    def evaluate_index_set(self, expr):
        array, index = self.resolve_index(expr)
        value = self.evaluate(expr.value)
        array[index] = value
        return value

    def resolve_index(self, expr):
        array = self.evaluate(expr.array)

        if not isinstance(array, list):
            raise CodeFabRuntimeError("Can only index into an array.")

        index = self.evaluate(expr.index)

        if not self.is_number(index):
            raise CodeFabRuntimeError("Array index must be a number.")

        if not float(index).is_integer():
            raise CodeFabRuntimeError("Array index must be an integer.")

        index = int(index)
        if index < 0 or index >= len(array):
            raise CodeFabRuntimeError("Array index out of range.")

        return array, index
