from .environment import Environment


class Callable:
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


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class UserFunction(Callable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def arity(self):
        return len(self.declaration.params)

    def call(self, executor, arguments):
        environment = Environment(self.closure)

        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param.origin, argument)

        try:
            executor.execute_block(self.declaration.body, environment)
        except ReturnSignal as return_signal:
            return return_signal.value

        return None

    def __repr__(self):
        return f"<fn {self.declaration.name.origin}>"