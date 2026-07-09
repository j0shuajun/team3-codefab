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

    def distance_to(self, name):
        """현재(가장 안쪽) 스코프 기준으로 이름이 몇 단계 위 스코프에 선언돼 있는지 반환한다.

        현재 스코프에 있으면 0, 그보다 한 단계 위면 1, ... 식이다.
        전역 스코프(스택의 맨 아래)에서 찾았거나 아예 못 찾았으면(=미선언) None 을 반환한다.
        전역 변수는 Executor 의 globals 환경에 항상 바로 있으므로 정적 바인딩 대상이 아니다.
        """
        scopes_from_innermost = list(reversed(self._scopes))
        global_depth = len(scopes_from_innermost) - 1

        for depth, scope in enumerate(scopes_from_innermost):
            if name in scope:
                return None if depth == global_depth else depth
        return None

    def mark_all_initialized(self):
        """지금 보이는 모든 스코프의 변수를 전부 초기화됨으로 표시한다.

        함수/메서드 본문은 선언 시점이 아니라 나중에(호출될 때) 실행되므로,
        본문을 resolve 하는 동안에는 바깥 스코프 변수의 "지금 이 순간" 초기화
        상태를 기준으로 미초기화 오류를 낼 수 없다 (호출 시점엔 이미 초기화돼
        있을 수도 있고, 그 반대일 수도 있어 정적으로 알 방법이 없다). 그래서
        본문을 resolve 하기 전 이 메서드로 바깥 변수를 전부 안전하게 만들어두고,
        끝나면 snapshot() 으로 떠둔 이전 상태로 restore() 해서 이 변화와 본문
        안에서 일어난 대입 효과 모두를 폐기한다.
        """
        for scope in self._scopes:
            for name in scope:
                scope[name] = True

    def snapshot(self):
        """현재 스코프 스택 상태를 복사해서 반환한다."""
        return [dict(scope) for scope in self._scopes]

    def restore(self, snapshot):
        """snapshot() 으로 저장해둔 상태로 스코프 스택을 되돌린다."""
        self._scopes = [dict(scope) for scope in snapshot]

    def _find_scope(self, name):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope
        return None
