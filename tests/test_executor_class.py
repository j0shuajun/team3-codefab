import pytest

from assembler.expr import (
    CallExpr,
    LiteralExpr,
    VariableExpr, SetExpr, GetExpr, ThisExpr,
)
from assembler.statement import (
    ExpressionStmt,
    PrintStmt,
    VarStmt, ClassStmt, FunctionStmt,
)
from assembler.tokenizer import Token, TokenType
from executor.executor import Executor


def token(token_type, origin, value=None):
    return Token(token_type, origin, value)


def run(statements):
    executor = Executor()
    executor.execute(statements)
    return executor


def test_create_instance_and_set_get_field():
    executor = run([
        ClassStmt(
            token(TokenType.IDENTIFIER, "Robot"),
            [],
        ),
        VarStmt(
            token(TokenType.IDENTIFIER, "r"),
            CallExpr(
                VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
                token(TokenType.RIGHT_PAREN, ")"),
                [],
            ),
        ),
        ExpressionStmt(
            SetExpr(
                VariableExpr(token(TokenType.IDENTIFIER, "r")),
                token(TokenType.IDENTIFIER, "name"),
                LiteralExpr("SpeedRobot"),
            )
        ),
        PrintStmt(
            GetExpr(
                VariableExpr(token(TokenType.IDENTIFIER, "r")),
                token(TokenType.IDENTIFIER, "name"),
            )
        ),
    ])

    assert executor.outputs == ["SpeedRobot"]


def test_method_call_uses_this():
    executor = run([
        ClassStmt(
            token(TokenType.IDENTIFIER, "Robot"),
            [
                FunctionStmt(
                    token(TokenType.IDENTIFIER, "report"),
                    [],
                    [
                        PrintStmt(
                            GetExpr(
                                ThisExpr(token(TokenType.THIS, "This")),
                                token(TokenType.IDENTIFIER, "name"),
                            )
                        )
                    ],
                )
            ],
        ),
        VarStmt(
            token(TokenType.IDENTIFIER, "r"),
            CallExpr(
                VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
                token(TokenType.RIGHT_PAREN, ")"),
                [],
            ),
        ),
        ExpressionStmt(
            SetExpr(
                VariableExpr(token(TokenType.IDENTIFIER, "r")),
                token(TokenType.IDENTIFIER, "name"),
                LiteralExpr("AndOr"),
            )
        ),
        ExpressionStmt(
            CallExpr(
                GetExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "r")),
                    token(TokenType.IDENTIFIER, "report"),
                ),
                token(TokenType.RIGHT_PAREN, ")"),
                [],
            )
        ),
    ])

    assert executor.outputs == ["AndOr"]
