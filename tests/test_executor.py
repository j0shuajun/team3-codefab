from assembler.expr import LiteralExpr
from assembler.statement import PrintStmt
from executor.executor import Executor


def run(statements):
    executor = Executor()
    executor.execute(statements)
    return executor


def test_print_literal_number():
    executor = run([
        PrintStmt(LiteralExpr(3))
    ])

    assert executor.outputs == ["3"]