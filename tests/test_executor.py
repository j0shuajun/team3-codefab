from assembler.expr import LiteralExpr, BinaryExpr, GroupingExpr, UnaryExpr, AssignExpr, VariableExpr
from assembler.statement import PrintStmt, VarStmt, ExpressionStmt
from assembler.tokenizer import Token, TokenType
from executor.executor import Executor


def token(token_type, origin):
    return Token(token_type, origin)


def run(statements):
    executor = Executor()
    executor.execute(statements)
    return executor


def test_print_literal_number():
    executor = run([
        PrintStmt(LiteralExpr(3))
    ])

    assert executor.outputs == ["3"]


def test_binary_expression_plus():
    executor = run([
        PrintStmt(
            BinaryExpr(
                LiteralExpr(3),
                token(TokenType.PLUS, "+"),
                LiteralExpr(2),
            )
        )
    ])

    assert executor.outputs == ["5"]

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

    executor = run([
        PrintStmt(expr)
    ])

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

    executor = run([
        PrintStmt(expr)
    ])

    assert executor.outputs == ["50"]


def test_unary_minus():
    executor = run([
        PrintStmt(
            UnaryExpr(
                token(TokenType.MINUS, "-"),
                LiteralExpr(3),
            )
        )
    ])

    assert executor.outputs == ["-3"]

def test_var_declaration_and_variable_reference():
    executor = run([
        VarStmt(token(TokenType.IDENTIFIER, "a"), LiteralExpr(10)),
        PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "a"))),
    ])

    assert executor.outputs == ["10"]


def test_assign_variable():
    executor = run([
        VarStmt(token(TokenType.IDENTIFIER, "a"), LiteralExpr(10)),
        ExpressionStmt(
            AssignExpr(
                token(TokenType.IDENTIFIER, "a"),
                LiteralExpr(20),
            )
        ),
        PrintStmt(VariableExpr(token(TokenType.IDENTIFIER, "a"))),
    ])

    assert executor.outputs == ["20"]

