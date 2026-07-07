from contextlib import contextmanager


class ScopeStack:
    """변수 선언/초기화 상태를 스코프 단위로 추적한다.

    각 스코프는 {변수명: 초기화 여부} 딕셔너리이며, 스택의 마지막 원소가
    현재(가장 안쪽) 스코프다.
    """

    def __init__(self):
        self._scopes = [{}]

    def reset(self):
        self._scopes = [{}]

    @contextmanager
    def new_scope(self):
        self._scopes.append({})
        try:
            yield
        finally:
            self._scopes.pop()

    def declare(self, name):
        """현재 스코프에 이름을 미초기화 상태로 선언한다.

        이미 현재 스코프에 같은 이름이 있으면 아무것도 하지 않고 False 를 반환한다.
        """
        scope = self._scopes[-1]
        if name in scope:
            return False
        scope[name] = False
        return True

    def initialize(self, name):
        """현재 스코프에 선언된 이름을 초기화 완료 상태로 바꾼다."""
        self._scopes[-1][name] = True

    def mark_initialized(self, name):
        """이름이 선언된 스코프를 안쪽부터 찾아 초기화 완료 상태로 바꾼다."""
        scope = self._find_scope(name)
        if scope is not None:
            scope[name] = True

    def is_uninitialized(self, name):
        """이름이 선언은 되었지만 아직 초기화되지 않았는지 확인한다."""
        scope = self._find_scope(name)
        return scope is not None and scope[name] is False

    def _find_scope(self, name):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope
        return None
