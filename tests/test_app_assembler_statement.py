from app.assembler.expr import LiteralExpr
from app.assembler.statement import (
    BlockStmt,
    ExpressionStmt,
    ForStmt,
    IfStmt,
    PrintStmt,
    VarStmt,
)
from app.assembler.tokenizer import Token, TokenType


def identifier(name):
    return Token(TokenType.IDENTIFIER, name)


def test_var_stmt_has_token_name_and_initializer():
    name = identifier("a")
    initializer = LiteralExpr(1)

    stmt = VarStmt(name, initializer)

    assert stmt.name == name
    assert stmt.initializer == initializer
    assert stmt.name.origin == "a"


def test_print_stmt_has_expression():
    expression = LiteralExpr(3)

    stmt = PrintStmt(expression)

    assert stmt.expression == expression


def test_expression_stmt_has_expression():
    expression = LiteralExpr(10)

    stmt = ExpressionStmt(expression)

    assert stmt.expression == expression


def test_block_stmt_has_statements():
    inner_stmt = PrintStmt(LiteralExpr(1))

    stmt = BlockStmt([inner_stmt])

    assert stmt.statements == [inner_stmt]


def test_if_stmt_has_condition_then_branch_and_else_branch():
    condition = LiteralExpr(True)
    then_branch = PrintStmt(LiteralExpr(1))
    else_branch = PrintStmt(LiteralExpr(2))

    stmt = IfStmt(condition, then_branch, else_branch)

    assert stmt.condition == condition
    assert stmt.then_branch == then_branch
    assert stmt.else_branch == else_branch


def test_for_stmt_has_initializer_condition_increment_and_body():
    initializer = VarStmt(identifier("i"), LiteralExpr(0))
    condition = LiteralExpr(True)
    increment = LiteralExpr(1)
    body = PrintStmt(LiteralExpr(100))

    stmt = ForStmt(initializer, condition, increment, body)

    assert stmt.initializer == initializer
    assert stmt.condition == condition
    assert stmt.increment == increment
    assert stmt.body == body
