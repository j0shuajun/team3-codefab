from abc import ABC, abstractmethod

from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from assembler.statement import BlockStmt, ExpressionStmt, ForStmt, IfStmt, VarStmt


class CodeFabTypeError(Exception):
    pass


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
        if resolver is None:
            raise CodeFabTypeError(f"Unknown expression type: {type(expr).__name__}")
        resolver(expr)

    def _resolve_variable_expr(self, expr):
        name = expr.name.origin
        if self._scopes.is_uninitialized(name):
            self._error_reporter.report(
                f"Variable '{name}' is used before initialization."
            )

    def _resolve_assign_expr(self, expr):
        self.resolve(expr.value)
        self._scopes.mark_initialized(expr.name.origin)

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
        self._resolvers = {
            VarStmt: self._resolve_var_stmt,
            BlockStmt: self._resolve_block_stmt,
            ExpressionStmt: self._resolve_expression_stmt,
            IfStmt: self._resolve_if_stmt,
            ForStmt: self._resolve_for_stmt,
        }

    def resolve_all(self, statements):
        for statement in statements:
            self.resolve(statement)

    def resolve(self, statement):
        resolver = self._resolvers.get(type(statement))
        if resolver is None:
            raise CodeFabTypeError(f"Unknown statement type: {type(statement).__name__}")
        resolver(statement)

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
        self.resolve(statement.then_branch)
        if statement.else_branch is not None:
            self.resolve(statement.else_branch)

    def _resolve_for_stmt(self, statement):
        if statement.initializer is not None:
            self.resolve(statement.initializer)
        if statement.condition is not None:
            self._expression_resolver.resolve(statement.condition)
        if statement.increment is not None:
            self._expression_resolver.resolve(statement.increment)
        self.resolve(statement.body)
