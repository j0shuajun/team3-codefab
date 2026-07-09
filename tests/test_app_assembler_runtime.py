import pytest

from app.assembler.expr import (
    BinaryExpr,
    CallExpr,
    GetExpr,
    LiteralExpr,
    VariableExpr,
)
from app.assembler.runtime import ImportedModule
from app.assembler.statement import (
    ClassStmt,
    PrintStmt,
    VarStmt,
)
from app.assembler.tokenizer import Token, TokenType
from app.executor.executor import CodeFabRuntimeError, Executor


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
        run(
            [
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
            ]
        )


def test_imported_module_get_returns_member():
    module = ImportedModule("sum", {"add": "some-function"})

    assert module.get(token(TokenType.IDENTIFIER, "add")) == "some-function"


def test_imported_module_get_unknown_member_raises():
    module = ImportedModule("sum", {"add": "some-function"})

    with pytest.raises(CodeFabRuntimeError):
        module.get(token(TokenType.IDENTIFIER, "missing"))


def test_get_expr_reads_imported_module_member():
    executor = Executor()
    executor.globals.define("sum", ImportedModule("sum", {"answer": 42}))

    executor.execute(
        [
            PrintStmt(
                GetExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "sum")),
                    token(TokenType.IDENTIFIER, "answer"),
                )
            )
        ]
    )

    assert executor.outputs == ["42"]


def test_runtime_error_superclass_must_be_class():
    with pytest.raises(RuntimeError):
        run(
            [
                VarStmt(
                    token(TokenType.IDENTIFIER, "NotClass"),
                    LiteralExpr(10),
                ),
                ClassStmt(
                    token(TokenType.IDENTIFIER, "Robot"),
                    [],
                    VariableExpr(token(TokenType.IDENTIFIER, "NotClass")),
                ),
            ]
        )
