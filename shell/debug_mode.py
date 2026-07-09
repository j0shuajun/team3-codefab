from dataclasses import dataclass

from assembler.assembler import Assembler
from assembler.environment import Environment
from assembler.statement import BlockStmt, ForStmt, IfStmt
from shell.shell import CodeFabRunner


@dataclass
class DebugFrame:
    statements: list
    index: int = 0
    previous_environment: object = None
    restore_environment: bool = False

    is_for_frame: bool = False
    for_stmt: object = None
    needs_increment: bool = False


class VariableStoreReader:
    def __init__(self, executor):
        self.executor = executor

    def lookup(self, name):
        environment = self.executor.environment

        while environment is not None:
            if name in environment.values:
                return environment.values[name]
            environment = environment.enclosing

        raise KeyError(name)

    def inspect_current_scope(self):
        return self.executor.environment.values


class DebugSession:
    def __init__(self, runner, statements):
        self.runner = runner
        self.frames = [DebugFrame(statements)]
        self.breakpoints = set()
        self.watch_names = []
        self.is_finished = False
        self.variable_reader = VariableStoreReader(runner.executor)
        self.last_break_stop_key = None

        self.normalize_frames()

    def process_command(self, command):
        command = command.strip()

        if command == "":
            return []

        command_name = command.split()[0].lower()

        if command_name in ("exit", "quit"):
            self.is_finished = True
            return ["Debug finished."]

        if command_name == "step":
            self.last_break_stop_key = None
            return (
                self.execute_current_statement(enter_block=True) + self.format_watches()
            )

        if command_name == "next":
            self.last_break_stop_key = None
            return (
                self.execute_current_statement(enter_block=False)
                + self.format_watches()
            )

        if command_name == "continue":
            return self.continue_until_breakpoint()

        if command_name == "break":
            return self.add_breakpoint(command)

        if command_name == "breakpoints":
            return self.show_breakpoints()

        if command_name == "remove":
            return self.remove_breakpoint(command)

        if command_name == "watch":
            return self.add_watch(command)

        if command_name == "unwatch":
            return self.remove_watch(command)

        if command_name == "watches":
            return self.format_watches(show_empty=True)

        if command_name == "inspect":
            return self.inspect_current_scope()

        return [f"Unknown debug command: {command}"]

    def execute_current_statement(self, enter_block):
        before_output_count = len(self.runner.executor.outputs)
        statement_line = None

        try:
            self.normalize_frames()

            if self.is_finished:
                return ["Program finished."]

            statement = self.current_statement()
            statement_line = getattr(statement, "line", None)

            if enter_block and isinstance(statement, BlockStmt):
                self.enter_block(statement)
                return []

            if enter_block and isinstance(statement, IfStmt):
                self.enter_if_branch(statement)
                return []

            if enter_block and isinstance(statement, ForStmt):
                self.enter_for_loop(statement)
                return []

            self.runner.executor.execute([statement])
            self.current_frame().index += 1
            self.normalize_frames()

            return self.runner.executor.outputs[before_output_count:]

        except Exception as error:
            self.is_finished = True
            outputs = self.runner.executor.outputs[before_output_count:]

            line = getattr(error, "line", None)
            if line is None:
                line = statement_line

            if line is None:
                return outputs + [f"Error: {error}"]

            return outputs + [f"Error at line {line}: {error}"]

    def enter_block(self, block_stmt):
        current_frame = self.current_frame()
        current_frame.index += 1

        previous_environment = self.runner.executor.environment
        block_environment = Environment(previous_environment)
        self.runner.executor.environment = block_environment

        self.frames.append(
            DebugFrame(
                block_stmt.statements,
                previous_environment=previous_environment,
                restore_environment=True,
            )
        )

        self.normalize_frames()

    def enter_if_branch(self, if_stmt):
        selected_branch = None

        if self.runner.executor.is_truthy(
            self.runner.executor.evaluate(if_stmt.condition)
        ):
            selected_branch = if_stmt.then_branch
        elif if_stmt.else_branch is not None:
            selected_branch = if_stmt.else_branch

        current_frame = self.current_frame()
        current_frame.index += 1

        if selected_branch is None:
            self.normalize_frames()
            return

        if isinstance(selected_branch, BlockStmt):
            previous_environment = self.runner.executor.environment
            block_environment = Environment(previous_environment)
            self.runner.executor.environment = block_environment

            self.frames.append(
                DebugFrame(
                    selected_branch.statements,
                    previous_environment=previous_environment,
                    restore_environment=True,
                )
            )
        else:
            self.frames.append(DebugFrame([selected_branch]))

        self.normalize_frames()

    def enter_for_loop(self, for_stmt):
        current_frame = self.current_frame()
        current_frame.index += 1

        previous_environment = self.runner.executor.environment
        loop_environment = Environment(previous_environment)
        self.runner.executor.environment = loop_environment

        if for_stmt.initializer is not None:
            self.runner.executor.execute([for_stmt.initializer])

        self.frames.append(
            DebugFrame(
                [],
                previous_environment=previous_environment,
                restore_environment=True,
                is_for_frame=True,
                for_stmt=for_stmt,
                needs_increment=False,
            )
        )

        self.normalize_frames()

    def continue_until_breakpoint(self):
        outputs = []

        while not self.is_finished:
            self.normalize_frames()

            if self.is_finished:
                break

            current_line = self.current_line()
            current_key = self.current_stop_key()

            if (
                current_line in self.breakpoints
                and self.last_break_stop_key != current_key
            ):
                self.last_break_stop_key = current_key
                return (
                    outputs
                    + [f"Stopped at breakpoint line {current_line}."]
                    + self.format_watches()
                )

            self.last_break_stop_key = None
            outputs.extend(self.execute_current_statement(enter_block=True))

        return outputs

    def add_breakpoint(self, command):
        line_number = self.parse_line_number(command)

        if line_number is None:
            return ["Usage: break <line_number>"]

        self.breakpoints.add(line_number)
        return [f"Breakpoint added at line {line_number}."]

    def remove_breakpoint(self, command):
        line_number = self.parse_line_number(command)

        if line_number is None:
            return ["Usage: remove <line_number>"]

        self.breakpoints.discard(line_number)
        return [f"Breakpoint removed at line {line_number}."]

    def show_breakpoints(self):
        if not self.breakpoints:
            return ["No breakpoints."]

        return [f"Breakpoints: {sorted(self.breakpoints)}"]

    def add_watch(self, command):
        parts = command.split(maxsplit=1)

        if len(parts) < 2 or parts[1].strip() == "":
            return ["Usage: watch <variable_name>"]

        variable_name = parts[1].strip()

        if variable_name not in self.watch_names:
            self.watch_names.append(variable_name)

        return [f"Watch added: {variable_name}"]

    def remove_watch(self, command):
        parts = command.split(maxsplit=1)

        if len(parts) < 2 or parts[1].strip() == "":
            return ["Usage: unwatch <variable_name>"]

        variable_name = parts[1].strip()

        if variable_name in self.watch_names:
            self.watch_names.remove(variable_name)

        return [f"Watch removed: {variable_name}"]

    def format_watches(self, show_empty=False):
        if not self.watch_names:
            return ["No watches."] if show_empty else []

        outputs = []

        for name in self.watch_names:
            try:
                value = self.variable_reader.lookup(name)
                outputs.append(f"{name} = {self.runner.executor.stringify(value)}")
            except KeyError:
                outputs.append(f"{name} = <undefined>")

        return outputs

    def inspect_current_scope(self):
        values = self.variable_reader.inspect_current_scope()

        if not values:
            return ["Current scope is empty."]

        outputs = []

        for name, value in values.items():
            outputs.append(f"{name} = {self.runner.executor.stringify(value)}")

        return outputs

    def normalize_frames(self):
        while self.frames:
            frame = self.current_frame()

            if frame.is_for_frame:
                self.normalize_for_frame(frame)
                continue

            if frame.index < len(frame.statements):
                break

            finished_frame = self.frames.pop()

            if finished_frame.restore_environment:
                self.runner.executor.environment = finished_frame.previous_environment

        if not self.frames:
            self.is_finished = True

    def normalize_for_frame(self, frame):
        for_stmt = frame.for_stmt

        if frame.needs_increment:
            self.execute_for_increment(for_stmt)
            frame.needs_increment = False

        if self.is_for_condition_truthy(for_stmt):
            self.push_for_body_frame(frame)
            return

        finished_frame = self.frames.pop()

        if finished_frame.restore_environment:
            self.runner.executor.environment = finished_frame.previous_environment

    def is_for_condition_truthy(self, for_stmt):
        if for_stmt.condition is None:
            return True

        try:
            return self.runner.executor.is_truthy(
                self.runner.executor.evaluate(for_stmt.condition)
            )
        except Exception as error:
            if getattr(error, "line", None) is None:
                error.line = getattr(for_stmt, "line", None)
            raise

    def execute_for_increment(self, for_stmt):
        if for_stmt.increment is None:
            return

        try:
            self.runner.executor.evaluate(for_stmt.increment)
        except Exception as error:
            if getattr(error, "line", None) is None:
                error.line = getattr(for_stmt, "line", None)
            raise

    def push_for_body_frame(self, frame):
        for_stmt = frame.for_stmt
        frame.needs_increment = True

        body = for_stmt.body

        if isinstance(body, BlockStmt):
            previous_environment = self.runner.executor.environment
            block_environment = Environment(previous_environment)
            self.runner.executor.environment = block_environment

            self.frames.append(
                DebugFrame(
                    body.statements,
                    previous_environment=previous_environment,
                    restore_environment=True,
                )
            )
            return

        self.frames.append(DebugFrame([body]))

    def current_frame(self):
        return self.frames[-1]

    def current_statement(self):
        if self.is_finished:
            return None

        frame = self.current_frame()
        return frame.statements[frame.index]

    def current_line(self):
        statement = self.current_statement()

        if statement is None:
            return None

        return getattr(statement, "line", None)

    def current_stop_key(self):
        statement = self.current_statement()

        if statement is None:
            return None

        return (len(self.frames), self.current_frame().index, id(statement))

    def parse_line_number(self, command):
        parts = command.split(maxsplit=1)

        if len(parts) < 2:
            return None

        raw_line_number = parts[1].strip()

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
        print(
            "Commands: step, next, continue, break <line>, breakpoints, remove <line>"
        )
        print("Commands: watch <name>, unwatch <name>, watches, inspect, exit")

        while not session.is_finished:
            line = session.current_line()
            statement = session.current_statement()

            if line is not None:
                print(f"(line {line}) {statement}")
            else:
                print(f"{statement}")

            command = input("(debug) ")
            outputs = session.process_command(command)

            for output in outputs:
                print(output)

    def run(self, file_path):
        outputs = self.run_file(file_path)

        for output in outputs:
            print(output)