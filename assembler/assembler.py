from .expr import LiteralExpr, BinaryExpr
from .statement import ExpressionStmt
from .tokenizer import TokenType


class AssemblerError(Exception):
    pass


class Assembler:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []

        while not self.is_at_end():
            statements.append(self.statement())

        return statements

    def statement(self):
        return self.expression_statement()

    def expression_statement(self):
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return ExpressionStmt(expression)

    def expression(self):
        return self.term()

    def primary(self):
        if self.match(TokenType.NUMBER):
            return LiteralExpr(self.previous().value)

        raise AssemblerError("Expected expression.")

    def match(self, *types):
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()
        raise AssemblerError(message)

    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def term(self):
        expr = self.factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def factor(self):
        expr = self.primary()

        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.primary()
            expr = BinaryExpr(expr, operator, right)

        return expr