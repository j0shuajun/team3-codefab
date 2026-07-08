from .expr import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    GetExpr,
    GroupingExpr,
    IndexGetExpr,
    IndexSetExpr,
    LiteralExpr,
    LogicalExpr,
    SetExpr,
    ThisExpr,
    UnaryExpr,
    VariableExpr,
)
from .statement import (
    BlockStmt,
    ClassStmt,
    ExpressionStmt,
    ForStmt,
    FunctionStmt,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    VarStmt,
)
from .tokenizer import TokenType


class AssemblerError(Exception):
    pass


# expression grammar
# assignment -> IDENTIFIER "=" assignment | logic_or
# logic_or   -> logic_and ("or" logic_and)*
# logic_and  -> equality ("and" equality)*
# equality   -> comparison (("!=" | "==") comparison)*
# comparison -> term ((">" | ">=" | "<" | "<=") term)*
# term       -> factor (("+" | "-") factor)*
# factor     -> unary (("*" | "/") unary)*
# unary      -> ("!" | "-") unary | primary
# primary    -> NUMBER | STRING | true | false | IDENTIFIER | "(" expression ")"


class Assembler:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def expression(self):
        return self.assignment()

    def parse(self):
        statements = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.RETURN):
            return self.return_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.FOR):
            return self.for_statement()

        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())

        return self.expression_statement()

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after for.")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")

        body = self.statement()

        return ForStmt(initializer, condition, increment, body)

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

    def assignment(self):
        expression = self.logic_or()

        if self.match(TokenType.EQUAL):
            value = self.assignment()

            if isinstance(expression, VariableExpr):
                return AssignExpr(expression.name, value)

            if isinstance(expression, GetExpr):
                return SetExpr(expression.object, expression.name, value)

            if isinstance(expression, IndexGetExpr):
                return IndexSetExpr(
                    expression.array, expression.bracket, expression.index, value
                )

            raise AssemblerError("Invalid assignment target.")

        return expression

    def logic_or(self):
        expression = self.logic_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expression = LogicalExpr(expression, operator, right)

        return expression

    def logic_and(self):
        expression = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expression = LogicalExpr(expression, operator, right)

        return expression

    def equality(self):
        expression = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = BinaryExpr(expression, operator, right)

        return expression

    def comparison(self):
        expression = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expression = BinaryExpr(expression, operator, right)

        return expression

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

        if self.match(TokenType.THIS):
            return ThisExpr(self.previous())

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

        return self.call()

    def declaration(self):
        if self.match(TokenType.CLASS):
            return self.class_declaration()

        if self.match(TokenType.FUNC):
            return self.function_declaration()

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

    def call(self):
        expression = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            elif self.match(TokenType.DOT):
                name = self.consume(
                    TokenType.IDENTIFIER, "Expected property name after '.'."
                )
                expression = GetExpr(expression, name)
                expr = self.finish_call(expr)
            elif self.match(TokenType.LEFT_BRACKET):
                expr = self.finish_index(expr)
            else:
                break

        return expression

    def finish_call(self, callee):
        arguments = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())

                if not self.match(TokenType.COMMA):
                    break

        paren = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments.")

        return CallExpr(callee, paren, arguments)

    def function_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected function name.")

        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name.")

        params = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                params.append(
                    self.consume(TokenType.IDENTIFIER, "Expected parameter name.")
                )

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before function body.")

        body = self.block()

        return FunctionStmt(name, params, body)

    def return_statement(self):
        keyword = self.previous()

        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after return value.")

        return ReturnStmt(keyword, value)

    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected class name.")

        self.consume(TokenType.LEFT_BRACE, "Expected '{' before class body.")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.method_declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after class body.")

        return ClassStmt(name, methods)

    def method_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected method name.")

        self.consume(TokenType.LEFT_PAREN, "Expected '(' after method name.")

        params = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                params.append(
                    self.consume(TokenType.IDENTIFIER, "Expected parameter name.")
                )

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before method body.")

        body = self.block()

        return FunctionStmt(name, params, body)

    def finish_index(self, array):
        index = self.expression()
        bracket = self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after index.")
        return IndexGetExpr(array, bracket, index)
