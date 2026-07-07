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


class PrintStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression


class VarStmt(Stmt):
    def __init__(self, name: Token, initializer: Optional[Expr] = None):
        self.name = name
        self.initializer = initializer


class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements


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
