from assembler.expr import LiteralExpr, BinaryExpr
from assembler.statement import PrintStmt
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

