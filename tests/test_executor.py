import pytest

from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from assembler.statement import (
    BlockStmt,
    ExpressionStmt,
    ForStmt,
    IfStmt,
    PrintStmt,
    VarStmt,
)
from assembler.tokenizer import Token, TokenType
from executor.executor import CodeFabRuntimeError, Executor


def token(token_type, origin):
    return Token(token_type, origin)


def run(statements):
    executor = Executor()
    executor.execute(statements)
    return executor


def test_print_literal_number():
    executor = run([PrintStmt(LiteralExpr(3))])

    assert executor.outputs == ["3"]


def test_binary_expression_plus():
    executor = run(
        [
            PrintStmt(
                BinaryExpr(
                    LiteralExpr(3),
                    token(TokenType.PLUS, "+"),
                    LiteralExpr(2),
                )
            )
        ]
    )

    assert executor.outputs == ["5"]


def test_binary_expression_greater():
    executor = run(
        [
            PrintStmt(
                BinaryExpr(
                    LiteralExpr(3),
                    token(TokenType.GREATER, ">"),
                    LiteralExpr(2),
                )
            )
        ]
    )

    assert executor.outputs == ["true"]


def test_binary_expression_greater_equal():
    executor = run(
        [
            PrintStmt(
                BinaryExpr(
                    LiteralExpr(3),
                    token(TokenType.GREATER_EQUAL, ">="),
                    LiteralExpr(2),
                )
            )
        ]
    )

    assert executor.outputs == ["true"]


def test_binary_expression_greater_equal2():
    executor = run(
        [
            PrintStmt(
                BinaryExpr(
                    LiteralExpr(3),
                    token(TokenType.GREATER_EQUAL, ">="),
                    LiteralExpr(3),
                )
            )
        ]
    )

    assert executor.outputs == ["true"]


def test_binary_expression_greater_type_diff():
    with pytest.raises(CodeFabRuntimeError):
        run(
            [
                PrintStmt(
                    BinaryExpr(
                        LiteralExpr(3),
                        token(TokenType.GREATER, ">"),
                        LiteralExpr("a"),
                    )
                )
            ]
        )


def test_binary_expression_greater_equal_type_diff():
    with pytest.raises(CodeFabRuntimeError):
        run(
            [
                PrintStmt(
                    BinaryExpr(
                        LiteralExpr(3),
                        token(TokenType.GREATER_EQUAL, ">="),
                        LiteralExpr("a"),
                    )
                )
            ]
        )


def test_binary_expression_less():
    executor = run(
        [
            PrintStmt(
                BinaryExpr(
                    LiteralExpr(1),
                    token(TokenType.LESS, "<"),
                    LiteralExpr(2),
                )
            )
        ]
    )

    assert executor.outputs == ["true"]


def test_binary_expression_less_equal():
    executor = run(
        [
            PrintStmt(
                BinaryExpr(
                    LiteralExpr(1),
                    token(TokenType.LESS_EQUAL, "<="),
                    LiteralExpr(2),
                )
            )
        ]
    )

    assert executor.outputs == ["true"]


def test_binary_expression_less_equal2():
    executor = run(
        [
            PrintStmt(
                BinaryExpr(
                    LiteralExpr(2),
                    token(TokenType.LESS_EQUAL, "<="),
                    LiteralExpr(2),
                )
            )
        ]
    )

    assert executor.outputs == ["true"]


def test_binary_expression_less_type_diff():
    with pytest.raises(CodeFabRuntimeError):
        run(
            [
                PrintStmt(
                    BinaryExpr(
                        LiteralExpr(3),
                        token(TokenType.LESS, "<"),
                        LiteralExpr("a"),
                    )
                )
            ]
        )


def test_binary_expression_less_equal_type_diff():
    with pytest.raises(CodeFabRuntimeError):
        run(
            [
                PrintStmt(
                    BinaryExpr(
                        LiteralExpr(3),
                        token(TokenType.LESS_EQUAL, "<="),
                        LiteralExpr("a"),
                    )
                )
            ]
        )


def test_operator_precedence_tree_is_respected():
    expr = BinaryExpr(
        LiteralExpr(3),
        token(TokenType.PLUS, "+"),
        BinaryExpr(
            LiteralExpr(7),
            token(TokenType.STAR, "*"),
            LiteralExpr(5),
        ),
    )

    executor = run([PrintStmt(expr)])

    assert executor.outputs == ["38"]


def test_grouping_expression():
    expr = BinaryExpr(
        GroupingExpr(
            BinaryExpr(
                LiteralExpr(3),
                token(TokenType.PLUS, "+"),
                LiteralExpr(7),
            )
        ),
        token(TokenType.STAR, "*"),
        LiteralExpr(5),
    )

    executor = run([PrintStmt(expr)])

    assert executor.outputs == ["50"]


def test_unary_minus():
    executor = run(
        [
            PrintStmt(
                UnaryExpr(
                    token(TokenType.MINUS, "-"),
                    LiteralExpr(3),
                )
            )
        ]
    )

    assert executor.outputs == ["-3"]


def test_var_declaration_and_variable_reference():
    executor = run(
        [
            VarStmt(token(TokenType.IDENTIFIER, "a"), LiteralExpr(10)),
            PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "a"))),
        ]
    )

    assert executor.outputs == ["10"]


def test_assign_variable():
    executor = run(
        [
            VarStmt(token(TokenType.IDENTIFIER, "a"), LiteralExpr(10)),
            ExpressionStmt(
                AssignExpr(
                    token(TokenType.IDENTIFIER, "a"),
                    LiteralExpr(20),
                )
            ),
            PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "a"))),
        ]
    )

    assert executor.outputs == ["20"]


def test_block_scope_can_access_global_variable():
    executor = run(
        [
            VarStmt(token(TokenType.IDENTIFIER, "a"), LiteralExpr(10)),
            BlockStmt(
                [
                    PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "a"))),
                ]
            ),
        ]
    )

    assert executor.outputs == ["10"]


def test_block_scope_local_variable_removed_after_block():
    statements = [
        BlockStmt(
            [
                VarStmt(token(TokenType.IDENTIFIER, "a"), LiteralExpr(10)),
            ]
        ),
        PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "a"))),
    ]

    with pytest.raises(CodeFabRuntimeError):
        run(statements)


def test_inner_scope_shadows_outer_scope():
    executor = run(
        [
            VarStmt(token(TokenType.IDENTIFIER, "a"), LiteralExpr(1)),
            BlockStmt(
                [
                    VarStmt(token(TokenType.IDENTIFIER, "a"), LiteralExpr(2)),
                    PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "a"))),
                ]
            ),
            PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "a"))),
        ]
    )

    assert executor.outputs == ["2", "1"]


def test_if_statement_then_branch():
    executor = run(
        [
            IfStmt(
                LiteralExpr(True),
                PrintStmt(LiteralExpr("then")),
                PrintStmt(LiteralExpr("else")),
            )
        ]
    )

    assert executor.outputs == ["then"]


def test_if_statement_else_branch():
    executor = run(
        [
            IfStmt(
                LiteralExpr(False),
                PrintStmt(LiteralExpr("then")),
                PrintStmt(LiteralExpr("else")),
            )
        ]
    )

    assert executor.outputs == ["else"]


def test_logical_and():
    executor = run(
        [
            PrintStmt(
                LogicalExpr(
                    LiteralExpr(True),
                    token(TokenType.AND, "and"),
                    LiteralExpr(False),
                )
            )
        ]
    )

    assert executor.outputs == ["false"]


def test_logical_or():
    executor = run(
        [
            PrintStmt(
                LogicalExpr(
                    LiteralExpr(False),
                    token(TokenType.OR, "or"),
                    LiteralExpr(True),
                )
            )
        ]
    )

    assert executor.outputs == ["true"]


def test_for_statement():
    executor = run(
        [
            ForStmt(
                VarStmt(token(TokenType.IDENTIFIER, "i"), LiteralExpr(0)),
                BinaryExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "i")),
                    token(TokenType.LESS, "<"),
                    LiteralExpr(3),
                ),
                AssignExpr(
                    token(TokenType.IDENTIFIER, "i"),
                    BinaryExpr(
                        VariableExpr(token(TokenType.IDENTIFIER, "i")),
                        token(TokenType.PLUS, "+"),
                        LiteralExpr(1),
                    ),
                ),
                PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "i"))),
            )
        ]
    )

    assert executor.outputs == ["0", "1", "2"]


def test_for_block_statement():
    executor = run(
        [
            ForStmt(
                VarStmt(token(TokenType.IDENTIFIER, "i"), LiteralExpr(0)),
                BinaryExpr(
                    VariableExpr(token(TokenType.IDENTIFIER, "i")),
                    token(TokenType.LESS, "<"),
                    LiteralExpr(3),
                ),
                AssignExpr(
                    token(TokenType.IDENTIFIER, "i"),
                    BinaryExpr(
                        VariableExpr(token(TokenType.IDENTIFIER, "i")),
                        token(TokenType.PLUS, "+"),
                        LiteralExpr(1),
                    ),
                ),
                BlockStmt(
                    [
                        PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "i"))),
                    ]
                ),
            )
        ]
    )

    assert executor.outputs == ["0", "1", "2"]


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
