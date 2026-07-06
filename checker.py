from statement import BlockStmt, VarStmt


class Checker:
    def __init__(self):
        self.errors = []
        self.scopes = []

    def check(self, statements):
        self.errors = []
        self.scopes = [set()]
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
            scope.add(statement.name)

    def _resolve_block_stmt(self, statement):
        self.scopes.append(set())
        self._resolve_statements(statement.statements)
        self.scopes.pop()
