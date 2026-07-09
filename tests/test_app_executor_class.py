from app.assembler.expr import (
    BinaryExpr,
    CallExpr,
    GetExpr,
    LiteralExpr,
    SetExpr,
    SuperExpr,
    ThisExpr,
    VariableExpr,
)
from app.assembler.statement import (
    ClassStmt,
    ExpressionStmt,
    FunctionStmt,
    PrintStmt,
    VarStmt,
)
from app.assembler.tokenizer import Token, TokenType
from app.executor.executor import Executor


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


def test_subclass_inherits_parent_method():
    executor = run(
        [
            ClassStmt(
                token(TokenType.IDENTIFIER, "Robot"),
                [
                    FunctionStmt(
                        token(TokenType.IDENTIFIER, "move"),
                        [],
                        [PrintStmt(LiteralExpr("move"))],
                    )
                ],
            ),
            ClassStmt(
                token(TokenType.IDENTIFIER, "SpeedRobot"),
                [],
                VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
            ),
            VarStmt(
                token(TokenType.IDENTIFIER, "r"),
                CallExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "SpeedRobot")),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [],
                ),
            ),
            ExpressionStmt(
                CallExpr(
                    GetExpr(
                        VariableExpr(token(TokenType.IDENTIFIER, "r")),
                        token(TokenType.IDENTIFIER, "move"),
                    ),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [],
                )
            ),
        ]
    )

    assert executor.outputs == ["move"]


def test_subclass_overrides_parent_method():
    executor = run(
        [
            ClassStmt(
                token(TokenType.IDENTIFIER, "Robot"),
                [
                    FunctionStmt(
                        token(TokenType.IDENTIFIER, "move"),
                        [],
                        [PrintStmt(LiteralExpr("parent move"))],
                    )
                ],
            ),
            ClassStmt(
                token(TokenType.IDENTIFIER, "SpeedRobot"),
                [
                    FunctionStmt(
                        token(TokenType.IDENTIFIER, "move"),
                        [],
                        [PrintStmt(LiteralExpr("child move"))],
                    )
                ],
                VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
            ),
            VarStmt(
                token(TokenType.IDENTIFIER, "r"),
                CallExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "SpeedRobot")),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [],
                ),
            ),
            ExpressionStmt(
                CallExpr(
                    GetExpr(
                        VariableExpr(token(TokenType.IDENTIFIER, "r")),
                        token(TokenType.IDENTIFIER, "move"),
                    ),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [],
                )
            ),
        ]
    )

    assert executor.outputs == ["child move"]


def test_super_method_call():
    executor = run(
        [
            ClassStmt(
                token(TokenType.IDENTIFIER, "Robot"),
                [
                    FunctionStmt(
                        token(TokenType.IDENTIFIER, "move"),
                        [],
                        [PrintStmt(LiteralExpr("move"))],
                    )
                ],
            ),
            ClassStmt(
                token(TokenType.IDENTIFIER, "SpeedRobot"),
                [
                    FunctionStmt(
                        token(TokenType.IDENTIFIER, "move"),
                        [],
                        [
                            ExpressionStmt(
                                CallExpr(
                                    SuperExpr(
                                        token(TokenType.SUPER, "Super"),
                                        token(TokenType.IDENTIFIER, "move"),
                                    ),
                                    token(TokenType.RIGHT_PAREN, ")"),
                                    [],
                                )
                            ),
                            PrintStmt(LiteralExpr("speed")),
                        ],
                    )
                ],
                VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
            ),
            VarStmt(
                token(TokenType.IDENTIFIER, "r"),
                CallExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "SpeedRobot")),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [],
                ),
            ),
            ExpressionStmt(
                CallExpr(
                    GetExpr(
                        VariableExpr(token(TokenType.IDENTIFIER, "r")),
                        token(TokenType.IDENTIFIER, "move"),
                    ),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [],
                )
            ),
        ]
    )

    assert executor.outputs == ["move", "speed"]


def test_instanceof_self_class():
    executor = run(
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
                BinaryExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "r")),
                    token(TokenType.INSTANCEOF, "instanceof"),
                    VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
                )
            ),
        ]
    )

    assert executor.outputs == ["true"]


def test_instanceof_parent_class():
    executor = run(
        [
            ClassStmt(token(TokenType.IDENTIFIER, "Robot"), []),
            ClassStmt(
                token(TokenType.IDENTIFIER, "SpeedRobot"),
                [],
                VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
            ),
            VarStmt(
                token(TokenType.IDENTIFIER, "r"),
                CallExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "SpeedRobot")),
                    token(TokenType.RIGHT_PAREN, ")"),
                    [],
                ),
            ),
            PrintStmt(
                BinaryExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "r")),
                    token(TokenType.INSTANCEOF, "instanceof"),
                    VariableExpr(token(TokenType.IDENTIFIER, "Robot")),
                )
            ),
        ]
    )

    assert executor.outputs == ["true"]
