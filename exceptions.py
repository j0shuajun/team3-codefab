class CodeFabRuntimeError(Exception):
    """Executor 가 프로그램을 실행하는 중에 발생하는 런타임 오류."""


class CodeFabTypeError(Exception):
    """Checker 가 알 수 없는 AST 노드 타입을 만났을 때 발생하는 오류."""
