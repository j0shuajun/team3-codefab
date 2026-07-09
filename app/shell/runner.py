from app.assembler.assembler import Assembler
from app.assembler.tokenizer import Tokenizer
from app.checker.checker import Checker
from app.executor.executor import Executor


class CodeFabRunner:
    def __init__(self, import_base_dir="."):
        self.tokenizer = Tokenizer()
        self.checker = Checker()
        self.executor = Executor(import_base_dir=import_base_dir)

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
