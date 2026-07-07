from checker.checker import Checker
from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from assembler.statement import BlockStmt, ExpressionStmt, ForStmt, IfStmt, VarStmt


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


class TestDfsTraversalOverControlFlow:
    def test_duplicate_declaration_detected_inside_if_branch(self):
        statements = [
            IfStmt(
                condition=LiteralExpr(True),
                then_branch=BlockStmt([
                    VarStmt("z", LiteralExpr(1)),
                    VarStmt("z", LiteralExpr(2)),
                ]),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "z" in errors[0]

    def test_uninitialized_access_detected_inside_else_branch(self):
        statements = [
            VarStmt("a"),
            IfStmt(
                condition=LiteralExpr(False),
                then_branch=BlockStmt([]),
                else_branch=BlockStmt([
                    ExpressionStmt(VariableExpr("a")),
                ]),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_self_reference_detected_inside_for_initializer(self):
        statements = [
            ForStmt(
                initializer=VarStmt("i", VariableExpr("i")),
                condition=None,
                increment=None,
                body=BlockStmt([]),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "i" in errors[0]

    def test_multiple_independent_errors_are_all_reported(self):
        statements = [
            VarStmt("a", VariableExpr("a")),
            VarStmt("b", LiteralExpr(1)),
            VarStmt("b", LiteralExpr(2)),
        ]

        errors = check(statements)

        assert len(errors) == 2
        assert any("a" in message for message in errors)
        assert any("b" in message for message in errors)


class TestComplexNestedTraversal:
    def test_duplicate_declaration_detected_four_levels_deep(self):
        statements = [
            BlockStmt([
                BlockStmt([
                    BlockStmt([
                        VarStmt("v", LiteralExpr(1)),
                        VarStmt("v", LiteralExpr(2)),
                    ]),
                ]),
            ]),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "v" in errors[0]

    def test_shadow_chain_only_flags_the_actual_duplicate(self):
        # 같은 이름 "v" 를 매 레벨마다 새로 선언(shadowing)하는 것은 허용되지만,
        # 가장 안쪽 스코프에서 같은 이름을 두 번 선언하는 것만 오류다.
        statements = [
            BlockStmt([
                VarStmt("v", LiteralExpr(0)),
                BlockStmt([
                    VarStmt("v", LiteralExpr(1)),
                    BlockStmt([
                        VarStmt("v", LiteralExpr(2)),
                        VarStmt("v", LiteralExpr(3)),
                    ]),
                ]),
            ]),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "v" in errors[0]

    def test_self_reference_buried_inside_complex_expression_tree(self):
        # a = !(1 + a) and true
        initializer = LogicalExpr(
            UnaryExpr("!", GroupingExpr(BinaryExpr(LiteralExpr(1), "+", VariableExpr("a")))),
            "and",
            LiteralExpr(True),
        )
        statements = [
            VarStmt("a", initializer),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_uninitialized_access_deep_inside_nested_for_and_if(self):
        statements = [
            VarStmt("count"),
            ForStmt(
                initializer=VarStmt("i", LiteralExpr(0)),
                condition=BinaryExpr(VariableExpr("i"), "<", LiteralExpr(10)),
                increment=AssignExpr("i", BinaryExpr(VariableExpr("i"), "+", LiteralExpr(1))),
                body=BlockStmt([
                    IfStmt(
                        condition=BinaryExpr(VariableExpr("i"), "==", LiteralExpr(5)),
                        then_branch=BlockStmt([
                            ExpressionStmt(VariableExpr("count")),
                        ]),
                    ),
                ]),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "count" in errors[0]

    def test_all_scattered_errors_across_branches_are_reported(self):
        # 서로 다른 가지(if-then, if-else, for-initializer)에 흩어진
        # 세 가지 종류의 오류가 모두 검출되어야 하고, 정상적인 코드는 오류로
        # 잘못 검출되면 안 된다.
        statements = [
            VarStmt("shared", LiteralExpr(1)),
            IfStmt(
                condition=VariableExpr("shared"),
                then_branch=BlockStmt([
                    VarStmt("dup", LiteralExpr(1)),
                    VarStmt("dup", LiteralExpr(2)),
                ]),
                else_branch=BlockStmt([
                    VarStmt("u"),
                    ExpressionStmt(VariableExpr("u")),
                ]),
            ),
            ForStmt(
                initializer=VarStmt("k", VariableExpr("k")),
                condition=None,
                increment=None,
                body=BlockStmt([
                    ExpressionStmt(VariableExpr("shared")),
                ]),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 3
        assert any("dup" in message for message in errors)
        assert any("u" in message for message in errors)
        assert any("k" in message for message in errors)

    def test_sibling_subtrees_do_not_leak_errors_into_each_other(self):
        # 한쪽 서브트리(then_branch)에서 발생한 오류가, 오류 없는 다른
        # 서브트리(else_branch)의 검사 결과에 영향을 주면 안 된다.
        statements = [
            IfStmt(
                condition=LiteralExpr(True),
                then_branch=BlockStmt([
                    VarStmt("dup", LiteralExpr(1)),
                    VarStmt("dup", LiteralExpr(2)),
                ]),
                else_branch=BlockStmt([
                    VarStmt("ok", LiteralExpr(1)),
                    ExpressionStmt(VariableExpr("ok")),
                ]),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "dup" in errors[0]