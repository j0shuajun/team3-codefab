from assembler.assembler import Assembler
from shell.shell import CodeFabRunner


class FileMode:
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
        before_output_count = len(self.runner.executor.outputs)

        try:
            tokens = self.runner.tokenizer.tokenize(source)
            statements = Assembler(tokens).parse()

            errors = self.runner.checker.check(statements)
            if errors:
                return errors

            return self.execute_statements_one_by_one(
                statements,
                before_output_count,
            )

        except Exception as error:
            outputs = self.runner.executor.outputs[before_output_count:]
            return outputs + [f"Error: {error}"]

    def execute_statements_one_by_one(self, statements, before_output_count):
        for statement in statements:
            try:
                self.runner.executor.execute([statement])
            except Exception as error:
                outputs = self.runner.executor.outputs[before_output_count:]
                line = getattr(statement, "line", None)

                if line is None:
                    return outputs + [f"Error: {error}"]

                return outputs + [f"Error at line {line}: {error}"]

        return self.runner.executor.outputs[before_output_count:]

    def run(self, file_path):
        outputs = self.run_file(file_path)

        for output in outputs:
            print(output)
