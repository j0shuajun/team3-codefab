class CodeFabRuntimeError(RuntimeError):
    def __init__(self, message, line=None):
        super().__init__(message)
        self.line = line


class CodeFabTypeError(TypeError):
    """Checker 가 알 수 없는 AST 노드 타입을 만났을 때 발생하는 오류."""
