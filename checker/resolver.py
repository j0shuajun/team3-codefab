from abc import ABC, abstractmethod
from enum import Enum, auto

from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    Expr,
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
from assembler.statement import (
    BlockStmt,
    ClassStmt,
    ExpressionStmt,
    ForStmt,
    FunctionStmt,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    Stmt,
    VarStmt,
)
from exceptions import CodeFabTypeError


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class ClassContext:
    """지금 클래스 본문(메서드) 안에서 resolve 중인지를 StatementResolver 와
    ExpressionResolver 가 공유하기 위한 상태. This/Super 는 어디서든(중첩된
    표현식 안에서도) 나타날 수 있어 ExpressionResolver 가 직접 검사해야 하지만,
    "지금 어떤 클래스 안에 있는지"는 ClassStmt 를 다루는 StatementResolver 만
    알 수 있으므로 이 작은 객체를 통해 상태를 공유한다."""

    def __init__(self):
        self.current = ClassType.NONE

    def reset(self):
        self.current = ClassType.NONE


class Resolver(ABC):
    @abstractmethod
    def resolve(self, node):
        raise NotImplementedError


class ExpressionResolver(Resolver):
    def __init__(self, scopes, error_reporter, class_context):
        self._scopes = scopes
        self._error_reporter = error_reporter
        self._class_context = class_context
        self._resolvers = {
            VariableExpr: self._resolve_variable_expr,
            AssignExpr: self._resolve_assign_expr,
            BinaryExpr: self._resolve_branching_expr,
            LogicalExpr: self._resolve_branching_expr,
            UnaryExpr: self._resolve_unary_expr,
            GroupingExpr: self._resolve_grouping_expr,
            LiteralExpr: self._resolve_literal_expr,
            IndexGetExpr: self._resolve_index_get_expr,
            IndexSetExpr: self._resolve_index_set_expr,
            ThisExpr: self._resolve_this_expr,
            SuperExpr: self._resolve_super_expr,
            CallExpr: self._resolve_call_expr,
            GetExpr: self._resolve_get_expr,
            SetExpr: self._resolve_set_expr,
        }

    def resolve(self, expr):
        resolver = self._resolvers.get(type(expr))
        if resolver is not None:
            resolver(expr)
            return

        if not isinstance(expr, Expr):
            raise CodeFabTypeError(f"Unknown expression type: {type(expr).__name__}")

    def _resolve_variable_expr(self, expr):
        name = expr.name.origin
        if self._scopes.is_uninitialized(name):
            self._error_reporter.report(
                f"Variable '{name}' is used before initialization."
            )
        expr.distance = self._scopes.distance_to(name)

    def _resolve_assign_expr(self, expr):
        self.resolve(expr.value)
        name = expr.name.origin
        self._scopes.mark_initialized(name)
        expr.distance = self._scopes.distance_to(name)

    def _resolve_branching_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def _resolve_unary_expr(self, expr):
        self.resolve(expr.right)

    def _resolve_grouping_expr(self, expr):
        self.resolve(expr.expression)

    def _resolve_literal_expr(self, expr):
        pass

    def _resolve_index_get_expr(self, expr):
        self.resolve(expr.array)
        self.resolve(expr.index)

    def _resolve_index_set_expr(self, expr):
        self.resolve(expr.array)
        self.resolve(expr.index)
        self.resolve(expr.value)

    def _resolve_this_expr(self, expr):
        if self._class_context.current == ClassType.NONE:
            self._error_reporter.report("Cannot use 'This' outside of a class.")

    def _resolve_super_expr(self, expr):
        if self._class_context.current == ClassType.NONE:
            self._error_reporter.report("Cannot use 'Super' outside of a class.")
        elif self._class_context.current != ClassType.SUBCLASS:
            self._error_reporter.report(
                "Cannot use 'Super' in a class with no superclass."
            )

    def _resolve_call_expr(self, expr):
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)

    def _resolve_get_expr(self, expr):
        self.resolve(expr.object)

    def _resolve_set_expr(self, expr):
        self.resolve(expr.object)
        self.resolve(expr.value)


class StatementResolver(Resolver):
    def __init__(self, scopes, error_reporter, expression_resolver, class_context):
        self._scopes = scopes
        self._error_reporter = error_reporter
        self._expression_resolver = expression_resolver
        self._class_context = class_context
        self._current_function = FunctionType.NONE
        self._resolvers = {
            VarStmt: self._resolve_var_stmt,
            BlockStmt: self._resolve_block_stmt,
            ExpressionStmt: self._resolve_expression_stmt,
            PrintStmt: self._resolve_expression_stmt,
            IfStmt: self._resolve_if_stmt,
            ForStmt: self._resolve_for_stmt,
            FunctionStmt: self._resolve_function_stmt,
            ReturnStmt: self._resolve_return_stmt,
            ClassStmt: self._resolve_class_stmt,
        }

    def reset(self):
        self._current_function = FunctionType.NONE
        self._class_context.reset()

    def resolve_all(self, statements):
        for statement in statements:
            self.resolve(statement)

    def resolve(self, statement):
        resolver = self._resolvers.get(type(statement))
        if resolver is not None:
            resolver(statement)
            return

        if not isinstance(statement, Stmt):
            raise CodeFabTypeError(
                f"Unknown statement type: {type(statement).__name__}"
            )

    def _resolve_var_stmt(self, statement):
        name = statement.name.origin
        if not self._scopes.declare(name):
            self._error_reporter.report(
                f"Variable '{name}' already declared in this scope."
            )

        if statement.initializer is not None:
            self._expression_resolver.resolve(statement.initializer)
            self._scopes.initialize(name)

    def _resolve_block_stmt(self, statement):
        with self._scopes.new_scope():
            self.resolve_all(statement.statements)

    def _resolve_expression_stmt(self, statement):
        self._expression_resolver.resolve(statement.expression)

    def _resolve_if_stmt(self, statement):
        self._expression_resolver.resolve(statement.condition)

        before = self._scopes.snapshot()
        self.resolve(statement.then_branch)
        then_snapshot = self._scopes.snapshot()

        if statement.else_branch is not None:
            self._scopes.restore(before)
            self.resolve(statement.else_branch)
            else_snapshot = self._scopes.snapshot()
        else:
            else_snapshot = before

        self._scopes.restore(self._merge_snapshots(then_snapshot, else_snapshot))

    @staticmethod
    def _merge_snapshots(then_snapshot, else_snapshot):
        """두 분기 모두에서 초기화된 변수만 초기화된 것으로 취급한다."""
        return [
            {
                name: initialized and else_scope.get(name, False)
                for name, initialized in then_scope.items()
            }
            for then_scope, else_scope in zip(then_snapshot, else_snapshot)
        ]

    def _resolve_for_stmt(self, statement):
        # Executor.execute_for 가 initializer 전용 loop_environment 를 새로 만드는 것과
        # 동일하게, Checker 도 for 문 전체를 위한 스코프를 하나 push 한다. 이렇게 해야
        # initializer 로 선언한 변수(i 등)가 for 문 밖으로 새지 않고, 정적 바인딩을 위해
        # 계산하는 distance 도 Executor 의 실제 Environment 중첩 깊이와 어긋나지 않는다.
        with self._scopes.new_scope():
            if statement.initializer is not None:
                self.resolve(statement.initializer)
            if statement.condition is not None:
                self._expression_resolver.resolve(statement.condition)

            # condition 이 처음부터 false 일 수 있어 body/increment 는 한 번도
            # 실행되지 않을 수 있다. 진입 전 상태를 남겨뒀다가, 반복문을 한 번이라도
            # 실행한 경우의 결과와 merge 해서 "루프 이후" 상태를 보수적으로 계산한다.
            before = self._scopes.snapshot()

            self.resolve(statement.body)
            if statement.increment is not None:
                self._expression_resolver.resolve(statement.increment)
            after_iteration = self._scopes.snapshot()

            self._scopes.restore(self._merge_snapshots(after_iteration, before))

    def _resolve_function_stmt(self, statement):
        name = statement.name.origin
        if not self._scopes.declare(name):
            self._error_reporter.report(
                f"Variable '{name}' already declared in this scope."
            )
        self._scopes.initialize(name)

        self._resolve_function_body(statement, FunctionType.FUNCTION)

    def _resolve_function_body(self, statement, function_type):
        enclosing_function = self._current_function
        self._current_function = function_type

        with self._scopes.new_scope():
            for param in statement.params:
                param_name = param.origin
                if not self._scopes.declare(param_name):
                    self._error_reporter.report(
                        f"Duplicate parameter name '{param_name}' in this function."
                    )
                self._scopes.initialize(param_name)

            self.resolve_all(statement.body)

        self._current_function = enclosing_function

    def _resolve_return_stmt(self, statement):
        if self._current_function == FunctionType.NONE:
            self._error_reporter.report("Cannot return from top-level code.")

        if self._current_function == FunctionType.INITIALIZER:
            self._error_reporter.report("Cannot return from an initializer.")

        if statement.value is not None:
            self._expression_resolver.resolve(statement.value)

    def _resolve_class_stmt(self, statement):
        name = statement.name.origin
        if not self._scopes.declare(name):
            self._error_reporter.report(
                f"Variable '{name}' already declared in this scope."
            )
        self._scopes.initialize(name)

        if statement.superclass is not None and statement.superclass.name.origin == name:
            self._error_reporter.report("A class can't inherit from itself.")

        enclosing_class = self._class_context.current
        self._class_context.current = ClassType.CLASS

        if statement.superclass is not None:
            self._class_context.current = ClassType.SUBCLASS
            self._expression_resolver.resolve(statement.superclass)

        for method in statement.methods:
            function_type = (
                FunctionType.INITIALIZER
                if method.name.origin == "init"
                else FunctionType.METHOD
            )
            self._resolve_function_body(method, function_type)

        self._class_context.current = enclosing_class
