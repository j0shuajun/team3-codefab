import pytest

from assembler.expr import CallExpr, LiteralExpr, VariableExpr
from assembler.statement import VarStmt
from assembler.tokenizer import Token, TokenType
from executor.executor import CodeFabRuntimeError, Executor

def test_array_creation():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    array_identifier = Token(TokenType.IDENTIFIER, "Array")
    right_paren = Token(TokenType.RIGHT_PAREN, ")")

    array_call = CallExpr(VariableExpr(array_identifier), right_paren, [LiteralExpr(3)])
    var_stmt = VarStmt(arr_name, array_call)

    executor = Executor()
    executor.execute([var_stmt])

    assert executor.environment.get(arr_name) == [None, None, None]


def test_array_creation_size_must_be_number():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    array_identifier = Token(TokenType.IDENTIFIER, "Array")
    right_paren = Token(TokenType.RIGHT_PAREN, ")")

    array_call = CallExpr(VariableExpr(array_identifier), right_paren, [LiteralExpr("hi")])
    var_stmt = VarStmt(arr_name, array_call)

    with pytest.raises(CodeFabRuntimeError, match="Array size must be a number."):
        executor = Executor()
        executor.execute([var_stmt])
