from assembler.expr import LiteralExpr
from assembler.statement import PrintStmt
from assembler.tokenizer import TokenType
from shell import PromptShell


class TemporaryParser:
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        first_token = self.tokens[0]

        if first_token.type == TokenType.NUMBER:
            return [PrintStmt(LiteralExpr(first_token.value))]

        return []


def main():
    shell = PromptShell(parser_class=TemporaryParser)
    shell.run()


if __name__ == "__main__":
    main()
