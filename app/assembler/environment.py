from app.exceptions import CodeFabRuntimeError


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name_token):
        return self.get_by_name(name_token.origin)

    def get_by_name(self, name):
        if name in self.values:
            return self.values[name]

        if self.enclosing is not None:
            return self.enclosing.get_by_name(name)

        raise CodeFabRuntimeError(f"Undefined variable '{name}'.")

    def assign(self, name_token, value):
        name = name_token.origin

        if name in self.values:
            self.values[name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name_token, value)
            return

        raise CodeFabRuntimeError(f"Undefined variable '{name}'.")

    def ancestor(self, distance):
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def get_at(self, distance, name):
        environment = self.ancestor(distance)
        if name not in environment.values:
            raise CodeFabRuntimeError(f"Undefined variable '{name}'.")
        return environment.values[name]

    def assign_at(self, distance, name, value):
        environment = self.ancestor(distance)
        if name not in environment.values:
            raise CodeFabRuntimeError(f"Undefined variable '{name}'.")
        environment.values[name] = value
