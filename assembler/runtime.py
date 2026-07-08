class Callable:
    """호출 가능한 런타임 객체의 공통 인터페이스"""

    def arity(self):
        raise NotImplementedError

    def call(self, executor, arguments):
        raise NotImplementedError


class NativeFunction(Callable):
    def __init__(self, name, arity, function):
        self.name = name
        self._arity = arity
        self.function = function

    def arity(self):
        return self._arity

    def call(self, executor, arguments):
        return self.function(*arguments)

    def __repr__(self):
        return f"<native fn {self.name}>"