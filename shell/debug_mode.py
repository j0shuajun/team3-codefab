from assembler.assembler import Assembler
from shell.shell import CodeFabRunner


class VariableStoreReader:
    ENV_ATTR_NAMES = ("environment", "env", "globals", "global_env")
    VALUE_ATTR_NAMES = ("values", "variables", "store")
    PARENT_ATTR_NAMES = ("enclosing", "parent", "outer")

    def __init__(self, executor):
        self.executor = executor

    def current_environment(self):
        for attr_name in self.ENV_ATTR_NAMES:
            if hasattr(self.executor, attr_name):
                return getattr(self.executor, attr_name)

        return None

    def get_values(self, environment):
        if environment is None:
            return {}

        if isinstance(environment, dict):
            return environment

        for attr_name in self.VALUE_ATTR_NAMES:
            values = getattr(environment, attr_name, None)
            if isinstance(values, dict):
                return values

        return {}

    def get_parent(self, environment):
        for attr_name in self.PARENT_ATTR_NAMES:
            if hasattr(environment, attr_name):
                return getattr(environment, attr_name)

        return None

    def lookup(self, name):
        environment = self.current_environment()

        while environment is not None:
            values = self.get_values(environment)

            if name in values:
                return values[name]

            environment = self.get_parent(environment)

        raise KeyError(name)

    def inspect_current_scope(self):
        environment = self.current_environment()

        if environment is None:
            return None

        return self.get_values(environment)


class DebugSession:
    def __init__(self, runner, statements):
        self.runner = runner
        self.statements = statements
        self.current_index = 0
        self.breakpoints = set()
        self.watch_names = []
        self.is_finished = False
        self.variable_reader = VariableStoreReader(runner.executor)

    def process_command(self, command):
        command = command.strip()

        if command in ("exit", "quit"):
            self.is_finished = True
            return ["Debug finished."]

        if command in ("step", "next"):
            return self.execute_current_statement() + self.format_watches()

        if command == "continue":
            return self.continue_until_breakpoint()

        if command.startswith("break "):
            return self.add_breakpoint(command)

        if command == "breakpoints":
            return self.show_breakpoints()

        if command.startswith("remove "):
            return self.remove_breakpoint(command)

        if command.startswith("watch "):
            return self.add_watch(command)

        if command.startswith("unwatch "):
            return self.remove_watch(command)

        if command == "watches":
            return self.format_watches()

        if command == "inspect":
            return self.inspect_current_scope()

        return [f"Unknown debug command: {command}"]

    def execute_current_statement(self):
        if self.is_finished or self.current_index >= len(self.statements):
            self.is_finished = True
            return ["Program finished."]

        before_output_count = len(self.runner.executor.outputs)
        statement = self.statements[self.current_index]

        try:
            self.runner.executor.execute([statement])
            self.current_index += 1

            if self.current_index >= len(self.statements):
                self.is_finished = True

            return self.runner.executor.outputs[before_output_count:]

        except Exception as error:
            self.is_finished = True
            outputs = self.runner.executor.outputs[before_output_count:]
            return outputs + [f"Error: {error}"]

    def continue_until_breakpoint(self):
        outputs = []

        while not self.is_finished:
            line = self.current_line()

            if line in self.breakpoints:
                outputs.append(f"Stopped at breakpoint line {line}.")
                outputs.extend(self.format_watches())
                return outputs

            outputs.extend(self.execute_current_statement())

        return outputs

    def add_breakpoint(self, command):
        line_number = self.parse_line_number(command, "break")
        if line_number is None:
            return ["Usage: break <line_number>"]

        self.breakpoints.add(line_number)
        return [f"Breakpoint added at line {line_number}."]

    def remove_breakpoint(self, command):
        line_number = self.parse_line_number(command, "remove")
        if line_number is None:
            return ["Usage: remove <line_number>"]

        self.breakpoints.discard(line_number)
        return [f"Breakpoint removed at line {line_number}."]

    def show_breakpoints(self):
        if not self.breakpoints:
            return ["No breakpoints."]

        breakpoints = sorted(self.breakpoints)
        return [f"Breakpoints: {breakpoints}"]

    def add_watch(self, command):
        variable_name = command.removeprefix("watch ").strip()

        if variable_name == "":
            return ["Usage: watch <variable_name>"]

        if variable_name not in self.watch_names:
            self.watch_names.append(variable_name)

        return [f"Watch added: {variable_name}"]

    def remove_watch(self, command):
        variable_name = command.removeprefix("unwatch ").strip()

        if variable_name == "":
            return ["Usage: unwatch <variable_name>"]

        if variable_name in self.watch_names:
            self.watch_names.remove(variable_name)

        return [f"Watch removed: {variable_name}"]

    def format_watches(self):
        if not self.watch_names:
            return ["No watches."]

        outputs = []

        for name in self.watch_names:
            try:
                value = self.variable_reader.lookup(name)
                outputs.append(f"{name} = {value}")
            except KeyError:
                outputs.append(f"{name} = <undefined>")

        return outputs

    def inspect_current_scope(self):
        values = self.variable_reader.inspect_current_scope()

        if values is None:
            return ["Current variable store is not accessible."]

        if not values:
            return ["Current scope is empty."]

        return [f"{name} = {value}" for name, value in values.items()]

    def current_line(self):
        statement = self.current_statement()
        return self.extract_statement_line(statement)

    def current_statement(self):
        if self.current_index >= len(self.statements):
            return None

        return self.statements[self.current_index]

    def extract_statement_line(self, statement):
        if statement is None:
            return None

        if hasattr(statement, "line"):
            return statement.line

        for attr_name in ("name", "keyword", "token", "operator"):
            attr = getattr(statement, attr_name, None)

            if attr is not None and hasattr(attr, "line"):
                return attr.line

        return None

    def parse_line_number(self, command, command_name):
        raw_line_number = command.removeprefix(command_name).strip()

        if not raw_line_number.isdigit():
            return None

        return int(raw_line_number)


class DebugMode:
    def __init__(self, runner=None):
        self.runner = runner or CodeFabRunner()

    def run_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                source = file.read()
        except FileNotFoundError:
            return [f"Error: file not found: {file_path}"]

        return self.run_source(source)

    def run_source(self, source):
        try:
            tokens = self.runner.tokenizer.tokenize(source)
            statements = Assembler(tokens).parse()

            errors = self.runner.checker.check(statements)
            if errors:
                return errors

            session = DebugSession(self.runner, statements)
            self.run_session(session)

            return []

        except Exception as error:
            return [f"Error: {error}"]

    def run_session(self, session):
        print("CodeFab Debug Mode")
        print("Commands: step, next, continue, break <line>, breakpoints, remove <line>")
        print("Commands: watch <name>, unwatch <name>, watches, inspect, exit")

        while not session.is_finished:
            line = session.current_line()
            if line is not None:
                print(f"(line {line})")

            command = input("(debug) ")
            outputs = session.process_command(command)

            for output in outputs:
                print(output)

    def run(self, file_path):
        outputs = self.run_file(file_path)

        for output in outputs:
            print(output)