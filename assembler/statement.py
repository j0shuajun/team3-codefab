from __future__ import annotations
from typing import Optional
from assembler.expr import Expr
from assembler.tokenizer import Token


class Stmt:
    """Base class for every statement node."""
    pass


class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStmt({self.expression})"


class PrintStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self):
        return f"PrintStmt({self.expression})"


class VarStmt(Stmt):
    def __init__(self, name: Token, initializer: Optional[Expr] = None):
        self.name = name
        self.initializer = initializer

    def __repr__(self):
        return f"VarStmt({self.name.origin}, {self.initializer})"


class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def __repr__(self):
        return f"BlockStmt({self.statements})"


class IfStmt(Stmt):
    def __init__(
        self,
        condition: Expr,
        then_branch: Stmt,
        else_branch: Optional[Stmt] = None,
    ):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return (
            f"IfStmt("
            f"condition={self.condition}, "
            f"then={self.then_branch}, "
            f"else={self.else_branch})"
        )


class ForStmt(Stmt):
    def __init__(
        self,
        initializer: Optional[Stmt],
        condition: Optional[Expr],
        increment: Optional[Expr],
        body: Stmt,
    ):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

    def __repr__(self):
        return (
            f"ForStmt("
            f"initializer={self.initializer}, "
            f"condition={self.condition}, "
            f"increment={self.increment}, "
            f"body={self.body})"
        )