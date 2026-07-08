"""정적 바인딩(static binding) 테스트.

1. Checker 가 VariableExpr/AssignExpr 에 정확한 distance 를 계산해서 부착하는지
   (트리에 대한 순수한 assertion)
2. Executor 가 distance 가 있으면 스코프 체인을 거슬러 올라가는 동적 조회
   (Environment.get/assign) 대신 미리 계산된 위치로 즉시 접근하는 경로
   (Environment.get_at/assign_at) 를 타는지 (Test Double 로 호출 경로 검증)
"""

import pytest

import executor.executor as executor_module
from assembler.expr import AssignExpr, LiteralExpr, VariableExpr
from assembler.statement import BlockStmt, ExpressionStmt, PrintStmt, VarStmt
from assembler.tokenizer import Token, TokenType
from checker.checker import Checker
from exceptions import CodeFabRuntimeError
from executor.executor import Environment, Executor


def token(origin):
    return Token(TokenType.IDENTIFIER, origin)


def resolve(statements):
    """Checker 를 돌려서 statements 트리에 distance 를 부착한다."""
    errors = Checker().check(statements)
    assert errors == []
    return statements


class SpyEnvironment(Environment):
    """Environment 의 어떤 조회 경로가 실제로 쓰였는지 기록하는 Test Double."""

    calls = []

    def get(self, name_token):
        SpyEnvironment.calls.append(("dynamic_get", name_token.origin))
        return super().get(name_token)

    def assign(self, name_token, value):
        SpyEnvironment.calls.append(("dynamic_assign", name_token.origin))
        super().assign(name_token, value)

    def get_at(self, distance, name):
        SpyEnvironment.calls.append(("static_get", distance, name))
        return super().get_at(distance, name)

    def assign_at(self, distance, name, value):
        SpyEnvironment.calls.append(("static_assign", distance, name))
        super().assign_at(distance, name, value)


def run_with_spy(statements, monkeypatch):
    SpyEnvironment.calls = []
    monkeypatch.setattr(executor_module, "Environment", SpyEnvironment)

    executor = Executor()
    executor.execute(statements)
    return executor


class TestCheckerComputesDistance:
    def test_variable_in_global_scope_has_no_distance(self):
        variable = VariableExpr(token("a"))
        resolve(
            [
                VarStmt(token("a"), LiteralExpr(1)),
                ExpressionStmt(variable),
            ]
        )

        assert variable.distance is None

    def test_global_variable_referenced_from_nested_block_still_has_no_distance(self):
        variable = VariableExpr(token("a"))
        resolve(
            [
                VarStmt(token("a"), LiteralExpr(1)),
                BlockStmt(
                    [
                        ExpressionStmt(variable),
                    ]
                ),
            ]
        )

        assert variable.distance is None

    def test_variable_declared_and_used_in_same_block_has_distance_zero(self):
        variable = VariableExpr(token("a"))
        resolve(
            [
                BlockStmt(
                    [
                        VarStmt(token("a"), LiteralExpr(1)),
                        ExpressionStmt(variable),
                    ]
                ),
            ]
        )

        assert variable.distance == 0

    def test_variable_used_one_block_below_declaration_has_distance_one(self):
        variable = VariableExpr(token("a"))
        resolve(
            [
                BlockStmt(
                    [
                        VarStmt(token("a"), LiteralExpr(1)),
                        BlockStmt(
                            [
                                ExpressionStmt(variable),
                            ]
                        ),
                    ]
                ),
            ]
        )

        assert variable.distance == 1

    def test_variable_used_two_blocks_below_declaration_has_distance_two(self):
        variable = VariableExpr(token("a"))
        resolve(
            [
                BlockStmt(
                    [
                        VarStmt(token("a"), LiteralExpr(1)),
                        BlockStmt(
                            [
                                BlockStmt(
                                    [
                                        ExpressionStmt(variable),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        )

        assert variable.distance == 2

    def test_inner_shadowing_variable_resolves_to_nearest_declaration(self):
        outer_read = VariableExpr(token("a"))
        inner_read = VariableExpr(token("a"))
        resolve(
            [
                BlockStmt(
                    [
                        VarStmt(token("a"), LiteralExpr(1)),
                        ExpressionStmt(outer_read),
                        BlockStmt(
                            [
                                VarStmt(token("a"), LiteralExpr(2)),
                                ExpressionStmt(inner_read),
                            ]
                        ),
                    ]
                ),
            ]
        )

        assert outer_read.distance == 0
        assert inner_read.distance == 0

    def test_assign_expr_distance_matches_declaration_scope(self):
        assignment = AssignExpr(token("a"), LiteralExpr(2))
        resolve(
            [
                BlockStmt(
                    [
                        VarStmt(token("a"), LiteralExpr(1)),
                        BlockStmt(
                            [
                                ExpressionStmt(assignment),
                            ]
                        ),
                    ]
                ),
            ]
        )

        assert assignment.distance == 1

    def test_for_loop_scope_counts_as_one_level_for_variables_used_in_body(self):
        # for 문 자체가 자기 스코프를 하나 갖기 때문에(Executor 의 loop_environment 와
        # 대응), initializer 로 선언한 변수를 body(자신의 BlockStmt) 안에서 읽으면
        # distance 는 1이어야 한다 (body 블록 -> for 스코프).
        from assembler.expr import BinaryExpr
        from assembler.statement import ForStmt

        loop_variable_read = VariableExpr(token("i"))
        resolve(
            [
                ForStmt(
                    initializer=VarStmt(token("i"), LiteralExpr(0)),
                    condition=BinaryExpr(
                        VariableExpr(token("i")), token("<"), LiteralExpr(3)
                    ),
                    increment=None,
                    body=BlockStmt(
                        [
                            ExpressionStmt(loop_variable_read),
                        ]
                    ),
                ),
            ]
        )

        assert loop_variable_read.distance == 1


class TestExecutorUsesStaticBindingWhenAvailable:
    def test_reading_local_variable_uses_get_at_not_dynamic_get(self, monkeypatch):
        statements = resolve(
            [
                BlockStmt(
                    [
                        VarStmt(token("a"), LiteralExpr(1)),
                        BlockStmt(
                            [
                                PrintStmt(VariableExpr(token("a"))),
                            ]
                        ),
                    ]
                ),
            ]
        )

        executor = run_with_spy(statements, monkeypatch)

        assert executor.outputs == ["1"]
        assert ("static_get", 1, "a") in SpyEnvironment.calls
        assert not any(
            call[0] == "dynamic_get" and call[1] == "a" for call in SpyEnvironment.calls
        )

    def test_assigning_local_variable_uses_assign_at_not_dynamic_assign(
        self, monkeypatch
    ):
        statements = resolve(
            [
                BlockStmt(
                    [
                        VarStmt(token("a"), LiteralExpr(1)),
                        BlockStmt(
                            [
                                ExpressionStmt(AssignExpr(token("a"), LiteralExpr(2))),
                                PrintStmt(VariableExpr(token("a"))),
                            ]
                        ),
                    ]
                ),
            ]
        )

        executor = run_with_spy(statements, monkeypatch)

        assert executor.outputs == ["2"]
        assert ("static_assign", 1, "a") in SpyEnvironment.calls
        assert not any(
            call[0] == "dynamic_assign" and call[1] == "a"
            for call in SpyEnvironment.calls
        )

    def test_global_variable_still_uses_dynamic_lookup(self, monkeypatch):
        # 전역 변수는 Checker 가 distance 를 붙이지 않으므로(=None), 지금까지와
        # 동일하게 동적 조회 경로를 그대로 타야 한다.
        statements = resolve(
            [
                VarStmt(token("a"), LiteralExpr(1)),
                PrintStmt(VariableExpr(token("a"))),
            ]
        )

        executor = run_with_spy(statements, monkeypatch)

        assert executor.outputs == ["1"]
        assert ("dynamic_get", "a") in SpyEnvironment.calls
        assert not any(call[0] == "static_get" for call in SpyEnvironment.calls)


class TestStaticBindingPreservesErrorSemantics:
    def test_get_at_raises_when_name_is_missing_in_target_environment(self):
        environment = Environment()

        with pytest.raises(CodeFabRuntimeError):
            environment.get_at(0, "a")

    def test_assign_at_raises_when_name_is_missing_in_target_environment(self):
        environment = Environment()

        with pytest.raises(CodeFabRuntimeError):
            environment.assign_at(0, "a", 1)

        assert "a" not in environment.values

    def test_get_at_succeeds_once_name_is_defined(self):
        environment = Environment()
        environment.define("a", 1)

        assert environment.get_at(0, "a") == 1

    def test_assign_at_succeeds_once_name_is_defined(self):
        environment = Environment()
        environment.define("a", 1)

        environment.assign_at(0, "a", 2)

        assert environment.values["a"] == 2

    def test_self_reference_via_assignment_in_initializer_still_raises_at_runtime(self):
        # { var a = a = 1; }
        # 초기화식(a = 1)이 평가되는 시점엔 아직 environment.define("a", ...) 가
        # 호출되기 전이라, distance 가 있어도(정적 바인딩) 동적 경로와 동일하게
        # "정의되지 않은 변수" 런타임 오류가 나야 한다.
        statements = resolve(
            [
                BlockStmt(
                    [
                        VarStmt(
                            token("a"),
                            AssignExpr(token("a"), LiteralExpr(1)),
                        ),
                    ]
                ),
            ]
        )

        with pytest.raises(CodeFabRuntimeError):
            Executor().execute(statements)
