
from assembler.expr import (
    CallExpr,
    GetExpr,
    LiteralExpr,
    SetExpr,
    ThisExpr,
    VariableExpr,
)
from assembler.statement import (
    ClassStmt,
    ExpressionStmt,
    FunctionStmt,
    PrintStmt,
    VarStmt,
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
    executor = run(
        [
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
        ]
    )

    assert executor.outputs == ["SpeedRobot"]


def test_method_call_uses_this():
    executor = run(
        [
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
        ]
    )

    assert executor.outputs == ["AndOr"]


def test_class_init_sets_field():
    executor = run(
        [
            ClassStmt(
                token(TokenType.IDENTIFIER, "Robot"),
                [
                    FunctionStmt(
                        token(TokenType.IDENTIFIER, "init"),
                        [token(TokenType.IDENTIFIER, "name")],
                        [
                            ExpressionStmt(
                                SetExpr(
                                    ThisExpr(token(TokenType.THIS, "This")),
                                    token(TokenType.IDENTIFIER, "name"),
                                    VariableExpr(token(TokenType.IDENTIFIER, "name")),
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
                    [LiteralExpr("AndOr")],
                ),
            ),
            PrintStmt(
                GetExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "r")),
                    token(TokenType.IDENTIFIER, "name"),
                )
            ),
        ]
    )

    assert executor.outputs == ["AndOr"]
