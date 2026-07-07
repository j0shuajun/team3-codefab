from assembler.expr import BinaryExpr, LiteralExpr, VariableExpr
from assembler.statement import BlockStmt, VarStmt


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
        elif isinstance(expr, BinaryExpr):
            self._resolve_expr(expr.left)
            self._resolve_expr(expr.right)
        elif isinstance(expr, LiteralExpr):
            pass

    def _resolve_variable_expr(self, expr):
        scope = self.scopes[-1]
        if scope.get(expr.name) is False:
            self.errors.append(
                f"Cannot reference variable '{expr.name}' in its own initializer."
            )
