import pytest

from assembler.expr import (
    CallExpr,
    IndexGetExpr,
    IndexSetExpr,
    LiteralExpr,
    VariableExpr,
)
from assembler.statement import PrintStmt, VarStmt
from assembler.tokenizer import Token, TokenType
from executor.executor import CodeFabRuntimeError, Executor

# ===== Array(3) 호출로 배열 생성 =====


def test_array_creation():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    array_identifier = Token(TokenType.IDENTIFIER, "Array")
    right_paren = Token(TokenType.RIGHT_PAREN, ")")

    array_size = 3
    array_call = CallExpr(
        VariableExpr(array_identifier), right_paren, [LiteralExpr(array_size)]
    )
    var_stmt = VarStmt(arr_name, array_call)

    executor = Executor()
    executor.execute([var_stmt])

    assert executor.environment.get(arr_name) == [None] * array_size


def test_array_creation_size_must_be_number():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    array_identifier = Token(TokenType.IDENTIFIER, "Array")
    right_paren = Token(TokenType.RIGHT_PAREN, ")")

    array_call = CallExpr(
        VariableExpr(array_identifier), right_paren, [LiteralExpr("hi")]
    )
    var_stmt = VarStmt(arr_name, array_call)

    with pytest.raises(CodeFabRuntimeError, match="Array size must be a number."):
        executor = Executor()
        executor.execute([var_stmt])


def test_array_creation_size_must_be_integer():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    array_identifier = Token(TokenType.IDENTIFIER, "Array")
    right_paren = Token(TokenType.RIGHT_PAREN, ")")

    array_call = CallExpr(
        VariableExpr(array_identifier), right_paren, [LiteralExpr(0.1)]
    )
    var_stmt = VarStmt(arr_name, array_call)

    with pytest.raises(CodeFabRuntimeError, match="Array size must be an integer."):
        executor = Executor()
        executor.execute([var_stmt])


def test_array_creation_size_must_not_be_negative():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    array_identifier = Token(TokenType.IDENTIFIER, "Array")
    right_paren = Token(TokenType.RIGHT_PAREN, ")")

    array_call = CallExpr(
        VariableExpr(array_identifier), right_paren, [LiteralExpr(-1)]
    )
    var_stmt = VarStmt(arr_name, array_call)

    with pytest.raises(CodeFabRuntimeError, match="Array size must not be negative."):
        executor = Executor()
        executor.execute([var_stmt])


# ===== IndexGetExpr로 배열 읽기 (arr[i]) =====


def test_array_index_get_returns_element():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_get = IndexGetExpr(VariableExpr(arr_name), bracket, LiteralExpr(0))
    executor.execute([PrintStmt(index_get)])

    assert executor.outputs == ["10"]


def test_array_index_get_out_of_range():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_get = IndexGetExpr(VariableExpr(arr_name), bracket, LiteralExpr(5))

    with pytest.raises(CodeFabRuntimeError, match="Array index out of range."):
        executor.execute([PrintStmt(index_get)])


def test_array_index_get_negative_index_out_of_range():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_get = IndexGetExpr(VariableExpr(arr_name), bracket, LiteralExpr(-1))

    with pytest.raises(CodeFabRuntimeError, match="Array index out of range."):
        executor.execute([PrintStmt(index_get)])


def test_array_index_get_index_must_be_number():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_get = IndexGetExpr(VariableExpr(arr_name), bracket, LiteralExpr("hello"))

    with pytest.raises(CodeFabRuntimeError, match="Array index must be a number."):
        executor.execute([PrintStmt(index_get)])


def test_array_index_get_index_must_be_integer():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_get = IndexGetExpr(VariableExpr(arr_name), bracket, LiteralExpr(0.9))

    with pytest.raises(CodeFabRuntimeError, match="Array index must be an integer."):
        executor.execute([PrintStmt(index_get)])


def test_array_index_get_target_must_be_array():
    x_name = Token(TokenType.IDENTIFIER, "x")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("x", 10)

    index_get = IndexGetExpr(VariableExpr(x_name), bracket, LiteralExpr(0))

    with pytest.raises(CodeFabRuntimeError, match="Can only index into an array."):
        executor.execute([PrintStmt(index_get)])


# ===== IndexSetExpr로 배열 쓰기 (arr[i] = value) =====


def test_array_index_set_updates_element():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    array = [10, 20, 30]
    executor.environment.define("arr", array)

    index_set = IndexSetExpr(
        VariableExpr(arr_name), bracket, LiteralExpr(0), LiteralExpr(99)
    )
    executor.execute([PrintStmt(index_set)])

    assert array == [99, 20, 30]
    assert executor.outputs == ["99"]


def test_array_index_set_out_of_range():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_set = IndexSetExpr(
        VariableExpr(arr_name), bracket, LiteralExpr(5), LiteralExpr(99)
    )

    with pytest.raises(CodeFabRuntimeError, match="Array index out of range."):
        executor.execute([PrintStmt(index_set)])


def test_array_index_set_negative_index_out_of_range():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_set = IndexSetExpr(
        VariableExpr(arr_name), bracket, LiteralExpr(-1), LiteralExpr(99)
    )

    with pytest.raises(CodeFabRuntimeError, match="Array index out of range."):
        executor.execute([PrintStmt(index_set)])


def test_array_index_set_index_must_be_number():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_set = IndexSetExpr(
        VariableExpr(arr_name), bracket, LiteralExpr("hello"), LiteralExpr(99)
    )

    with pytest.raises(CodeFabRuntimeError, match="Array index must be a number."):
        executor.execute([PrintStmt(index_set)])


def test_array_index_set_index_must_be_integer():
    arr_name = Token(TokenType.IDENTIFIER, "arr")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("arr", [10, 20, 30])

    index_set = IndexSetExpr(
        VariableExpr(arr_name), bracket, LiteralExpr(0.9), LiteralExpr(99)
    )

    with pytest.raises(CodeFabRuntimeError, match="Array index must be an integer."):
        executor.execute([PrintStmt(index_set)])


def test_array_index_set_target_must_be_array():
    x_name = Token(TokenType.IDENTIFIER, "x")
    bracket = Token(TokenType.RIGHT_BRACKET, "]")

    executor = Executor()
    executor.environment.define("x", 10)

    index_set = IndexSetExpr(
        VariableExpr(x_name), bracket, LiteralExpr(0), LiteralExpr(99)
    )

    with pytest.raises(CodeFabRuntimeError, match="Can only index into an array."):
        executor.execute([PrintStmt(index_set)])
