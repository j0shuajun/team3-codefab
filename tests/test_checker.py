from assembler.expr import LiteralExpr
from assembler.statement import BlockStmt, VarStmt
from checker import Checker


def check(statements):
    return Checker().check(statements)


class TestDuplicateDeclaration:
    def test_duplicate_declaration_in_global_scope_is_error(self):
        statements = [
            VarStmt("a", LiteralExpr(1)),
            VarStmt("a", LiteralExpr(2)),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_unique_declarations_produce_no_error(self):
        statements = [
            VarStmt("a", LiteralExpr(1)),
            VarStmt("b", LiteralExpr(2)),
        ]

        assert check(statements) == []

    def test_duplicate_declaration_inside_same_block_is_error(self):
        statements = [
            BlockStmt(
                [
                    VarStmt("x", LiteralExpr(1)),
                    VarStmt("x", LiteralExpr(2)),
                ]
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "x" in errors[0]

    def test_shadowing_in_nested_block_is_allowed(self):
        statements = [
            VarStmt("x", LiteralExpr(1)),
            BlockStmt(
                [
                    VarStmt("x", LiteralExpr(2)),
                ]
            ),
        ]

        assert check(statements) == []

    def test_sibling_blocks_may_reuse_same_name(self):
        statements = [
            BlockStmt([VarStmt("x", LiteralExpr(1))]),
            BlockStmt([VarStmt("x", LiteralExpr(2))]),
        ]

        assert check(statements) == []
