from .expr import BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr, VariableExpr, AssignExpr, LogicalExpr
from .statement import ExpressionStmt, PrintStmt, VarStmt, BlockStmt, IfStmt
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
            statements.append(self.declaration())

        return statements

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())

        return self.expression_statement()

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after if.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")

        then_branch = self.statement()

        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return IfStmt(condition, then_branch, else_branch)

    def block(self):
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def print_statement(self):
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return PrintStmt(expression)

    def expression_statement(self):
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return ExpressionStmt(expression)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logic_or()

        if self.match(TokenType.EQUAL):
            value = self.assignment()

            if isinstance(expr, VariableExpr):
                return AssignExpr(expr.name, value)

            raise AssemblerError("Invalid assignment target.")

        return expr

    def logic_or(self):
        expr = self.logic_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def logic_and(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match(
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def primary(self):
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)

        if self.match(TokenType.TRUE):
            return LiteralExpr(True)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().value)

        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return GroupingExpr(expression)

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
        expression = self.factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expression = BinaryExpr(expression, operator, right)

        return expression

    def factor(self):
        expression = self.unary()

        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()
            expression = BinaryExpr(expression, operator, right)

        return expression

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpr(operator, right)

        return self.primary()

    def declaration(self):
        if self.match(TokenType.VAR):
            return self.var_declaration()

        return self.statement()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return VarStmt(name, initializer)
