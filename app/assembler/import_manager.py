import os
from contextlib import contextmanager

from app.assembler.assembler import Assembler
from app.assembler.statement import ClassStmt, FunctionStmt, ImportStmt, VarStmt
from app.assembler.tokenizer import Tokenizer
from app.exceptions import CodeFabRuntimeError

ALLOWED_IMPORT_STATEMENTS = (ImportStmt, FunctionStmt, ClassStmt, VarStmt)


class ImportManager:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self._cache = {}
        self._stack = []

    def resolve_path(self, path, base_dir=None):
        base = base_dir if base_dir is not None else self.base_dir
        combined = path if os.path.isabs(path) else os.path.join(base, path)
        return os.path.abspath(combined)

    def read(self, path, base_dir=None):
        resolved = self.resolve_path(path, base_dir)

        if resolved not in self._cache:
            if not os.path.isfile(resolved):
                raise CodeFabRuntimeError(f"Import target not found: {path}")

            with open(resolved, "r", encoding="utf-8") as file:
                self._cache[resolved] = file.read()

        return self._cache[resolved]

    def load(self, path, base_dir=None):
        source = self.read(path, base_dir)
        statements = Assembler(Tokenizer().tokenize(source)).parse()

        for statement in statements:
            if not isinstance(statement, ALLOWED_IMPORT_STATEMENTS):
                raise CodeFabRuntimeError(
                    f"Import target '{path}' may only contain import, "
                    "Func, Class, or var declarations."
                )

        return statements

    @contextmanager
    def importing(self, path, base_dir=None):
        resolved = self.resolve_path(path, base_dir)

        if resolved in self._stack:
            chain = " -> ".join(self._stack + [resolved])
            raise CodeFabRuntimeError(f"Circular import detected: {chain}")

        self._stack.append(resolved)
        try:
            yield resolved
        finally:
            self._stack.pop()
