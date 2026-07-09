from collections import Counter

from assembler.assembler import Assembler
from assembler.tokenizer import Tokenizer
from checker.checker import Checker
from executor.executor import Executor


class CodeFabRunner:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.checker = Checker()
        self.executor = Executor()

    def run_code(self, source):
        before_output_count = len(self.executor.outputs)

        try:
            tokens = self.tokenizer.tokenize(source)
            statements = Assembler(tokens).parse()

            errors = self.checker.check(statements)
            if errors:
                return errors

            self.executor.execute(statements)

            return self.executor.outputs[before_output_count:]

        except Exception as error:
            outputs = self.executor.outputs[before_output_count:]
            return outputs + [f"Error: {error}"]


class ExplainMode:
    def explain_source(self, source):
        runner = CodeFabRunner()
        outputs = []

        try:
            tokens = runner.tokenizer.tokenize(source)
            outputs.extend(self.format_tokens(tokens))

            statements = Assembler(tokens).parse()
            outputs.extend(self.format_ast(statements))

            errors = runner.checker.check(statements)
            outputs.extend(self.format_checker(errors))

            if errors:
                return outputs

            before_output_count = len(runner.executor.outputs)
            before_values = dict(runner.executor.environment.values)

            runner.executor.execute(statements)

            execution_outputs = runner.executor.outputs[before_output_count:]
            changed_values = self.find_changed_values(
                before_values,
                runner.executor.environment.values,
            )

            outputs.extend(
                self.format_result(
                    runner,
                    execution_outputs,
                    changed_values,
                )
            )

            return outputs

        except Exception as error:
            outputs.append("")
            outputs.append("[Result]")
            outputs.append(f"Error: {error}")
            return outputs

    def format_tokens(self, tokens):
        token_names = []

        for token in tokens:
            token_names.append(token.type.name)

        return [
            "[Tokens]",
            " ".join(token_names),
            "",
        ]

    def format_ast(self, statements):
        outputs = [
            "[AST]",
        ]

        if not statements:
            outputs.append("<empty>")
        elif len(statements) == 1:
            outputs.append(str(statements[0]))
        else:
            for statement in statements:
                outputs.append(str(statement))

        outputs.append("")
        return outputs

    def format_checker(self, errors):
        outputs = [
            "[Checker]",
        ]

        if errors:
            outputs.extend(errors)
        else:
            outputs.append("No errors")

        outputs.append("")
        return outputs

    def find_changed_values(self, before_values, after_values):
        changed_values = {}

        for name, value in after_values.items():
            if name not in before_values:
                changed_values[name] = value
                continue

            if before_values[name] != value:
                changed_values[name] = value

        return changed_values

    def format_result(self, runner, execution_outputs, changed_values):
        outputs = [
            "[Result]",
        ]

        if execution_outputs:
            outputs.append("[Output]")
            outputs.extend(execution_outputs)

        if changed_values:
            if execution_outputs:
                outputs.append("")

            outputs.append("[Variables]")
            for name, value in changed_values.items():
                outputs.append(f"{name} = {runner.executor.stringify(value)}")

        if not execution_outputs and not changed_values:
            outputs.append("No output")

        return outputs


class PromptShell:
    EXIT_COMMANDS = ("exit", "quit")
    EXPLAIN_COMMAND = "explain"

    def __init__(self, history_size=10):
        self.runner = CodeFabRunner()
        self.explainer = ExplainMode()

        self.history_size = history_size
        self.history = []
        self.recommended_command = None
        self.is_running = True

    def run(self):
        print("CodeFab Prompt Shell")
        print("Type exit or quit to quit, ctrlc to recommend, ctrlv to rerun.")
        print("Type explain <code> to inspect the CodeFab pipeline.")

        while self.is_running:
            source = input("CodeFab> ")
            outputs = self.run_line(source)

            for output in outputs:
                print(output)

    def run_line(self, source):
        source = source.strip()

        if source == "":
            return []

        shell_outputs = self.run_shell_command(source)
        if shell_outputs is not None:
            return shell_outputs

        self.save_history(source)
        return self.run_code(source)

    def run_shell_command(self, source):
        if source in self.EXIT_COMMANDS:
            self.is_running = False
            return ["Bye!"]

        if source == "ctrlc":
            return self.recommend_command()

        if source == "ctrlv":
            return self.run_recommended_command()

        if source == self.EXPLAIN_COMMAND:
            return ["Usage: explain <code>"]

        if source.startswith(f"{self.EXPLAIN_COMMAND} "):
            code = source[len(self.EXPLAIN_COMMAND) :].strip()

            if code == "":
                return ["Usage: explain <code>"]

            return self.explainer.explain_source(code)

        return None

    def run_code(self, source):
        return self.runner.run_code(source)

    def save_history(self, source):
        self.history.append(source)

        if len(self.history) > self.history_size:
            self.history.pop(0)

    def recommend_command(self):
        if not self.history:
            return ["추천할 명령어가 없습니다."]

        command_counts = Counter(self.history)
        max_count = max(command_counts.values())

        for command in reversed(self.history):
            if command_counts[command] == max_count:
                self.recommended_command = command
                return [
                    f"Ctrl+C 추천 명령어: {command}",
                    "ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.",
                ]

        return ["추천할 명령어가 없습니다."]

    def run_recommended_command(self):
        if self.recommended_command is None:
            return ["먼저 ctrlc 로 추천 명령어를 생성해주세요."]

        return self.run_code(self.recommended_command)


ReplMode = PromptShell
