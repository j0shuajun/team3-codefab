from __future__ import annotations

from typing import Optional

from assembler.expr import Expr
from assembler.tokenizer import Token


class Stmt:
    """Base class for every statement node."""

    def __init__(self, line=None):
        self.line = line


class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr, line=None):
        super().__init__(line)
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStmt({self.expression})"


class PrintStmt(Stmt):
    def __init__(self, expression: Expr, line=None):
        super().__init__(line)
        self.expression = expression

    def __repr__(self):
        return f"PrintStmt({self.expression})"


class VarStmt(Stmt):
    def __init__(self, name: Token, initializer: Optional[Expr] = None, line=None):
        super().__init__(line if line is not None else getattr(name, "line", None))
        self.name = name
        self.initializer = initializer

    def __repr__(self):
        return f"VarStmt({self.name.origin}, {self.initializer})"


class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt], line=None):
        super().__init__(line)
        self.statements = statements

    def __repr__(self):
        return f"BlockStmt({self.statements})"


class IfStmt(Stmt):
    def __init__(
        self,
        condition: Expr,
        then_branch: Stmt,
        else_branch: Optional[Stmt] = None,
        line=None,
    ):
        super().__init__(line)
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
        line=None,
    ):
        super().__init__(line)
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


class FunctionStmt(Stmt):
    """Func name(params) { body } 함수 선언문"""

    def __init__(self, name: Token, params: list[Token], body: list[Stmt], line=None):
        super().__init__(line if line is not None else getattr(name, "line", None))
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        param_names = [param.origin for param in self.params]
        return (
            f"FunctionStmt({self.name.origin}, params={param_names}, body={self.body})"
        )


class ReturnStmt(Stmt):
    """return expression; 문장"""

    def __init__(self, keyword: Token, value: Optional[Expr] = None, line=None):
        super().__init__(line if line is not None else getattr(keyword, "line", None))
        self.keyword = keyword
        self.value = value

    def __repr__(self):
        return f"ReturnStmt({self.value})"


class ClassStmt(Stmt):
    """Class Name (: SuperClass)? { methods... } 클래스 선언문"""

    def __init__(
        self,
        name: Token,
        methods: list[FunctionStmt],
        superclass=None,
        line=None,
    ):
        super().__init__(line if line is not None else getattr(name, "line", None))
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def __repr__(self):
        superclass_name = None
        if self.superclass is not None:
            superclass_name = self.superclass.name.origin

        return (
            f"ClassStmt("
            f"{self.name.origin}, "
            f"superclass={superclass_name}, "
            f"methods={self.methods})"
        )
