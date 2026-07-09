from exceptions import CodeFabRuntimeError

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

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("This", instance)
        return UserFunction(self.declaration, environment)

    def __repr__(self):
        return f"<fn {self.declaration.name.origin}>"


class UserClass(Callable):
    def __init__(self, name, methods, superclass=None):
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]

        if self.superclass is not None:
            return self.superclass.find_method(name)

        return None

    def arity(self):
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def call(self, executor, arguments):
        instance = UserInstance(self)

        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(executor, arguments)

        return instance

    def __repr__(self):
        return f"<class {self.name}>"


class UserInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name_token):
        name = name_token.origin

        if name in self.fields:
            return self.fields[name]

        method = self.klass.find_method(name)
        if method is not None:
            return method.bind(self)

        raise CodeFabRuntimeError(f"Undefined property '{name}'.")

    def set(self, name_token, value):
        self.fields[name_token.origin] = value

    def is_instance_of(self, klass):
        current = self.klass

        while current is not None:
            if current is klass:
                return True
            current = current.superclass

        return False

    def __repr__(self):
        return f"<{self.klass.name} instance>"
