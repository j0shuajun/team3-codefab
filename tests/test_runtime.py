import pytest

from assembler.expr import (
    BinaryExpr,
    CallExpr,
    LiteralExpr,
    VariableExpr, GetExpr,
)
from assembler.statement import (
    PrintStmt, ClassStmt, VarStmt,
)
from assembler.tokenizer import Token, TokenType
from executor.executor import CodeFabRuntimeError, Executor


def token(token_type, origin, value=None):
    return Token(token_type, origin, value)


def run(statements):
    executor = Executor()
    executor.execute(statements)
    return executor


def test_runtime_error_undefined_variable():
    with pytest.raises(CodeFabRuntimeError):
        run([PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "x")))])


def test_runtime_error_divide_by_zero():
    with pytest.raises(CodeFabRuntimeError):
        run(
            [
                PrintStmt(
                    BinaryExpr(
                        LiteralExpr(3),
                        token(TokenType.SLASH, "/"),
                        LiteralExpr(0),
                    )
                )
            ]
        )


def test_runtime_error_type_mismatch():
    with pytest.raises(CodeFabRuntimeError):
        run(
            [
                PrintStmt(
                    BinaryExpr(
                        LiteralExpr(3),
                        token(TokenType.MINUS, "-"),
                        LiteralExpr("hello"),
                    )
                )
            ]
        )


def test_execute_native_call_expression():
    executor = run(
        [
            PrintStmt(
                CallExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "add")),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [
                        LiteralExpr(3),
                        LiteralExpr(7),
                    ],
                )
            )
        ]
    )

    assert executor.outputs == ["10"]


def test_runtime_error_call_non_callable():
    with pytest.raises(RuntimeError):
        run(
            [
                PrintStmt(
                    CallExpr(
                        LiteralExpr("hello"),
                        token(TokenType.RIGHT_PAREN, ")"),
                        [],
                    )
                )
            ]
        )


def test_runtime_error_call_argument_count_mismatch():
    with pytest.raises(RuntimeError):
        run(
            [
                PrintStmt(
                    CallExpr(
                        VariableExpr(token(TokenType.IDENTIFIER, "add")),
                        token(TokenType.RIGHT_PAREN, ")"),
                        [LiteralExpr(1)],
                    )
                )
            ]
        )

def test_runtime_error_get_unknown_property():
    with pytest.raises(RuntimeError):
        run([
            ClassStmt(token(TokenType.IDENTIFIER, "Robot"), []),
            VarStmt(
                token(TokenType.IDENTIFIER, "r"),
                CallExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [],
                ),
            ),
            PrintStmt(
                GetExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "r")),
                    token(TokenType.IDENTIFIER, "power"),
                )
            ),
        ])

