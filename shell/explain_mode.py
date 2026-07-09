from assembler.assembler import Assembler
from shell.shell import CodeFabRunner


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
