import os
from contextlib import contextmanager

from app.exceptions import CodeFabRuntimeError


class ImportManager:
    """import 대상 파일을 읽고, 순환 import 를 감지한다.

    같은 scope 내 중복 import, alias 이름 충돌, 반복문 내 import 금지처럼
    "어느 scope 에서 실행됐는가"를 알아야 하는 검사는 다루지 않는다. 이 클래스는
    "경로 -> 파일 내용" 변환과 "지금 import 체인 안에서 같은 파일을 다시 열려고
    하는가"만 책임진다.
    """

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
