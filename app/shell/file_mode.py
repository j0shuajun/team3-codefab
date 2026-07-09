import os

from app.assembler.assembler import Assembler
from app.shell.runner import CodeFabRunner


class FileMode:
    def __init__(self, runner=None):
        self.runner = runner

    def run_file(self, file_path):
        absolute_path = os.path.abspath(file_path)
        import_base_dir = os.path.dirname(absolute_path)

        try:
            with open(absolute_path, "r", encoding="utf-8") as file:
                source = file.read()
        except FileNotFoundError:
            return [f"Error: file not found: {file_path}"]

        runner = self.runner or CodeFabRunner(import_base_dir=import_base_dir)
        return self.run_source(source, runner)

    def run_source(self, source, runner=None):
        active_runner = runner or self.runner or CodeFabRunner()
        before_output_count = len(active_runner.executor.outputs)

        try:
            tokens = active_runner.tokenizer.tokenize(source)
            statements = Assembler(tokens).parse()

            errors = active_runner.checker.check(statements)
            if errors:
                return errors

            return self.execute_statements_one_by_one(
                active_runner,
                statements,
                before_output_count,
            )

        except Exception as error:
            outputs = active_runner.executor.outputs[before_output_count:]
            return outputs + [f"Error: {error}"]

    def execute_statements_one_by_one(
        self,
        runner,
        statements,
        before_output_count,
    ):
        for statement in statements:
            try:
                runner.executor.execute([statement])
            except Exception as error:
                outputs = runner.executor.outputs[before_output_count:]

                line = getattr(error, "line", None)
                if line is None:
                    line = getattr(statement, "line", None)

                if line is None:
                    return outputs + [f"Error: {error}"]

                return outputs + [f"Error at line {line}: {error}"]

        return runner.executor.outputs[before_output_count:]

    def run(self, file_path):
        outputs = self.run_file(file_path)

        for output in outputs:
            print(output)
