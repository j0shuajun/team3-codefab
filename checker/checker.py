from assembler.expr import AssignExpr, BinaryExpr, LiteralExpr, VariableExpr
from assembler.statement import BlockStmt, ExpressionStmt, VarStmt


class Checker:
    def __init__(self):
        self.errors = []
        self.scopes = []

    def check(self, statements):
        self.errors = []
        self.scopes = [{}]
        self._resolve_statements(statements)
        return self.errors

    def _resolve_statements(self, statements):
        for statement in statements:
            self._resolve_statement(statement)

    def _resolve_statement(self, statement):
        if isinstance(statement, VarStmt):
            self._resolve_var_stmt(statement)
        elif isinstance(statement, BlockStmt):
            self._resolve_block_stmt(statement)
        elif isinstance(statement, ExpressionStmt):
            self._resolve_expr(statement.expression)

    def _resolve_var_stmt(self, statement):
        scope = self.scopes[-1]
        if statement.name in scope:
            self.errors.append(
                f"Variable '{statement.name}' already declared in this scope."
            )
        else:
            scope[statement.name] = False

        if statement.initializer is not None:
            self._resolve_expr(statement.initializer)
            scope[statement.name] = True

    def _resolve_block_stmt(self, statement):
        self.scopes.append({})
        self._resolve_statements(statement.statements)
        self.scopes.pop()

    def _resolve_expr(self, expr):
        if isinstance(expr, VariableExpr):
            self._resolve_variable_expr(expr)
        elif isinstance(expr, AssignExpr):
            self._resolve_assign_expr(expr)
        elif isinstance(expr, BinaryExpr):
            self._resolve_expr(expr.left)
            self._resolve_expr(expr.right)
        elif isinstance(expr, LiteralExpr):
            pass

    def _resolve_variable_expr(self, expr):
        for scope in reversed(self.scopes):
            if expr.name in scope:
                if scope[expr.name] is False:
                    self.errors.append(
                        f"Variable '{expr.name}' is used before initialization."
                    )
                return

    def _resolve_assign_expr(self, expr):
        self._resolve_expr(expr.value)
        for scope in reversed(self.scopes):
            if expr.name in scope:
                scope[expr.name] = True
                return
