from abc import ABC, abstractmethod
from enum import Enum, auto

from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from assembler.statement import (
    BlockStmt,
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


class Resolver(ABC):
    @abstractmethod
    def resolve(self, node):
        raise NotImplementedError


class ExpressionResolver(Resolver):
    def __init__(self, scopes, error_reporter):
        self._scopes = scopes
        self._error_reporter = error_reporter
        self._resolvers = {
            VariableExpr: self._resolve_variable_expr,
            AssignExpr: self._resolve_assign_expr,
            BinaryExpr: self._resolve_branching_expr,
            LogicalExpr: self._resolve_branching_expr,
            UnaryExpr: self._resolve_unary_expr,
            GroupingExpr: self._resolve_grouping_expr,
            LiteralExpr: self._resolve_literal_expr,
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


class StatementResolver(Resolver):
    def __init__(self, scopes, error_reporter, expression_resolver):
        self._scopes = scopes
        self._error_reporter = error_reporter
        self._expression_resolver = expression_resolver
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
        }

    def reset(self):
        self._current_function = FunctionType.NONE

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

        if statement.value is not None:
            self._expression_resolver.resolve(statement.value)
