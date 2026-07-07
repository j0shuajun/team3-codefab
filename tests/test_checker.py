from checker.checker import Checker
from assembler.expr import LiteralExpr, VariableExpr, BinaryExpr, AssignExpr
from assembler.statement import BlockStmt, VarStmt, ExpressionStmt


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
            BlockStmt([
                VarStmt("x", LiteralExpr(1)),
                VarStmt("x", LiteralExpr(2)),
            ]),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "x" in errors[0]

    def test_shadowing_in_nested_block_is_allowed(self):
        statements = [
            VarStmt("x", LiteralExpr(1)),
            BlockStmt([
                VarStmt("x", LiteralExpr(2)),
            ]),
        ]

        assert check(statements) == []

    def test_sibling_blocks_may_reuse_same_name(self):
        statements = [
            BlockStmt([VarStmt("x", LiteralExpr(1))]),
            BlockStmt([VarStmt("x", LiteralExpr(2))]),
        ]

        assert check(statements) == []


class TestSelfReferenceInInitializer:
    def test_direct_self_reference_is_error(self):
        statements = [
            VarStmt("a", VariableExpr("a")),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_self_reference_inside_expression_is_error(self):
        statements = [
            VarStmt("a", BinaryExpr(VariableExpr("a"), "+", LiteralExpr(1))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_initializer_referencing_other_declared_variable_is_allowed(self):
        statements = [
            VarStmt("a", LiteralExpr(1)),
            VarStmt("b", VariableExpr("a")),
        ]

        assert check(statements) == []

    def test_self_reference_inside_nested_block_is_error(self):
        statements = [
            BlockStmt([
                VarStmt("y", VariableExpr("y")),
            ]),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "y" in errors[0]


class TestUninitializedVariableAccess:
    def test_reading_uninitialized_variable_is_error(self):
        statements = [
            VarStmt("a"),
            ExpressionStmt(VariableExpr("a")),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_reading_initialized_variable_is_allowed(self):
        statements = [
            VarStmt("a", LiteralExpr(1)),
            ExpressionStmt(VariableExpr("a")),
        ]

        assert check(statements) == []

    def test_variable_becomes_initialized_after_assignment(self):
        statements = [
            VarStmt("a"),
            ExpressionStmt(AssignExpr("a", LiteralExpr(1))),
            ExpressionStmt(VariableExpr("a")),
        ]

        assert check(statements) == []
