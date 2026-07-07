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


class CheckerError(Exception):
    """Checker 가 처리할 수 없는 노드를 만났을 때 발생하는 예외."""


class Checker:
    def __init__(self):
        self.errors = []
        self.scopes = []
        self._statement_resolvers = {
            VarStmt: self._resolve_var_stmt,
            BlockStmt: self._resolve_block_stmt,
            ExpressionStmt: self._resolve_expression_stmt,
            IfStmt: self._resolve_if_stmt,
            ForStmt: self._resolve_for_stmt,
        }
        self._expr_resolvers = {
            VariableExpr: self._resolve_variable_expr,
            AssignExpr: self._resolve_assign_expr,
            BinaryExpr: self._resolve_branching_expr,
            LogicalExpr: self._resolve_branching_expr,
            UnaryExpr: self._resolve_unary_expr,
            GroupingExpr: self._resolve_grouping_expr,
            LiteralExpr: self._resolve_literal_expr,
        }

    def check(self, statements):
        self.errors = []
        self.scopes = [{}]
        self._resolve_statements(statements)
        return self.errors

    def _resolve_statements(self, statements):
        for statement in statements:
            self._resolve_statement(statement)

    def _resolve_statement(self, statement):
        resolver = self._statement_resolvers.get(type(statement))
        if resolver is None:
            raise CheckerError(f"Unknown statement type: {type(statement).__name__}")
        resolver(statement)

    def _resolve_expr(self, expr):
        resolver = self._expr_resolvers.get(type(expr))
        if resolver is None:
            raise CheckerError(f"Unknown expression type: {type(expr).__name__}")
        resolver(expr)

    # --- statement resolvers -------------------------------------------------

    def _resolve_var_stmt(self, statement):
        name = statement.name.origin
        scope = self.scopes[-1]

        if name in scope:
            self.errors.append(f"Variable '{name}' already declared in this scope.")
        else:
            scope[name] = False

        if statement.initializer is not None:
            self._resolve_expr(statement.initializer)
            scope[name] = True

    def _resolve_block_stmt(self, statement):
        self.scopes.append({})
        try:
            self._resolve_statements(statement.statements)
        finally:
            self.scopes.pop()

    def _resolve_expression_stmt(self, statement):
        self._resolve_expr(statement.expression)

    def _resolve_if_stmt(self, statement):
        self._resolve_expr(statement.condition)
        self._resolve_statement(statement.then_branch)
        if statement.else_branch is not None:
            self._resolve_statement(statement.else_branch)

    def _resolve_for_stmt(self, statement):
        if statement.initializer is not None:
            self._resolve_statement(statement.initializer)
        if statement.condition is not None:
            self._resolve_expr(statement.condition)
        if statement.increment is not None:
            self._resolve_expr(statement.increment)
        self._resolve_statement(statement.body)

    # --- expression resolvers -------------------------------------------------

    def _resolve_branching_expr(self, expr):
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def _resolve_unary_expr(self, expr):
        self._resolve_expr(expr.right)

    def _resolve_grouping_expr(self, expr):
        self._resolve_expr(expr.expression)

    def _resolve_literal_expr(self, expr):
        pass

    def _resolve_variable_expr(self, expr):
        name = expr.name.origin
        scope = self._find_declaring_scope(name)
        if scope is not None and scope[name] is False:
            self.errors.append(f"Variable '{name}' is used before initialization.")

    def _resolve_assign_expr(self, expr):
        self._resolve_expr(expr.value)
        name = expr.name.origin
        scope = self._find_declaring_scope(name)
        if scope is not None:
            scope[name] = True

    # --- helpers -------------------------------------------------

    def _find_declaring_scope(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope
        return None
