from app.assembler.expr import (
    AssignExpr,
    BinaryExpr,
    GroupingExpr,
    IndexGetExpr,
    IndexSetExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from app.assembler.statement import BlockStmt, ExpressionStmt, ForStmt, IfStmt, VarStmt
from app.assembler.tokenizer import Token, TokenType
from app.checker.checker import Checker


def token(origin):
    return Token(TokenType.IDENTIFIER, origin)


def bracket():
    return Token(TokenType.RIGHT_BRACKET, "]")


def check(statements):
    return Checker().check(statements)


class TestDuplicateDeclaration:
    def test_duplicate_declaration_in_global_scope_is_error(self):
        statements = [
            VarStmt(token("a"), LiteralExpr(1)),
            VarStmt(token("a"), LiteralExpr(2)),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_unique_declarations_produce_no_error(self):
        statements = [
            VarStmt(token("a"), LiteralExpr(1)),
            VarStmt(token("b"), LiteralExpr(2)),
        ]

        assert check(statements) == []

    def test_duplicate_declaration_inside_same_block_is_error(self):
        statements = [
            BlockStmt(
                [
                    VarStmt(token("x"), LiteralExpr(1)),
                    VarStmt(token("x"), LiteralExpr(2)),
                ]
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "x" in errors[0]

    def test_shadowing_in_nested_block_is_allowed(self):
        statements = [
            VarStmt(token("x"), LiteralExpr(1)),
            BlockStmt(
                [
                    VarStmt(token("x"), LiteralExpr(2)),
                ]
            ),
        ]

        assert check(statements) == []

    def test_sibling_blocks_may_reuse_same_name(self):
        statements = [
            BlockStmt([VarStmt(token("x"), LiteralExpr(1))]),
            BlockStmt([VarStmt(token("x"), LiteralExpr(2))]),
        ]

        assert check(statements) == []


class TestSelfReferenceInInitializer:
    def test_direct_self_reference_is_error(self):
        statements = [
            VarStmt(token("a"), VariableExpr(token("a"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_self_reference_inside_expression_is_error(self):
        statements = [
            VarStmt(
                token("a"),
                BinaryExpr(VariableExpr(token("a")), token("+"), LiteralExpr(1)),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_initializer_referencing_other_declared_variable_is_allowed(self):
        statements = [
            VarStmt(token("a"), LiteralExpr(1)),
            VarStmt(token("b"), VariableExpr(token("a"))),
        ]

        assert check(statements) == []

    def test_self_reference_inside_nested_block_is_error(self):
        statements = [
            BlockStmt(
                [
                    VarStmt(token("y"), VariableExpr(token("y"))),
                ]
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "y" in errors[0]


class TestUninitializedVariableAccess:
    def test_reading_uninitialized_variable_is_error(self):
        statements = [
            VarStmt(token("a")),
            ExpressionStmt(VariableExpr(token("a"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_reading_initialized_variable_is_allowed(self):
        statements = [
            VarStmt(token("a"), LiteralExpr(1)),
            ExpressionStmt(VariableExpr(token("a"))),
        ]

        assert check(statements) == []

    def test_variable_becomes_initialized_after_assignment(self):
        statements = [
            VarStmt(token("a")),
            ExpressionStmt(AssignExpr(token("a"), LiteralExpr(1))),
            ExpressionStmt(VariableExpr(token("a"))),
        ]

        assert check(statements) == []


class TestDfsTraversalOverControlFlow:
    def test_duplicate_declaration_detected_inside_if_branch(self):
        statements = [
            IfStmt(
                condition=LiteralExpr(True),
                then_branch=BlockStmt(
                    [
                        VarStmt(token("z"), LiteralExpr(1)),
                        VarStmt(token("z"), LiteralExpr(2)),
                    ]
                ),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "z" in errors[0]

    def test_uninitialized_access_detected_inside_else_branch(self):
        statements = [
            VarStmt(token("a")),
            IfStmt(
                condition=LiteralExpr(False),
                then_branch=BlockStmt([]),
                else_branch=BlockStmt(
                    [
                        ExpressionStmt(VariableExpr(token("a"))),
                    ]
                ),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_self_reference_detected_inside_for_initializer(self):
        statements = [
            ForStmt(
                initializer=VarStmt(token("i"), VariableExpr(token("i"))),
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
            VarStmt(token("a"), VariableExpr(token("a"))),
            VarStmt(token("b"), LiteralExpr(1)),
            VarStmt(token("b"), LiteralExpr(2)),
        ]

        errors = check(statements)

        assert len(errors) == 2
        assert any("a" in message for message in errors)
        assert any("b" in message for message in errors)


class TestComplexNestedTraversal:
    def test_duplicate_declaration_detected_four_levels_deep(self):
        statements = [
            BlockStmt(
                [
                    BlockStmt(
                        [
                            BlockStmt(
                                [
                                    VarStmt(token("v"), LiteralExpr(1)),
                                    VarStmt(token("v"), LiteralExpr(2)),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "v" in errors[0]

    def test_shadow_chain_only_flags_the_actual_duplicate(self):
        # 같은 이름 "v" 를 매 레벨마다 새로 선언(shadowing)하는 것은 허용되지만,
        # 가장 안쪽 스코프에서 같은 이름을 두 번 선언하는 것만 오류다.
        statements = [
            BlockStmt(
                [
                    VarStmt(token("v"), LiteralExpr(0)),
                    BlockStmt(
                        [
                            VarStmt(token("v"), LiteralExpr(1)),
                            BlockStmt(
                                [
                                    VarStmt(token("v"), LiteralExpr(2)),
                                    VarStmt(token("v"), LiteralExpr(3)),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "v" in errors[0]

    def test_self_reference_buried_inside_complex_expression_tree(self):
        # a = !(1 + a) and true
        initializer = LogicalExpr(
            UnaryExpr(
                token("!"),
                GroupingExpr(
                    BinaryExpr(LiteralExpr(1), token("+"), VariableExpr(token("a")))
                ),
            ),
            token("and"),
            LiteralExpr(True),
        )
        statements = [
            VarStmt(token("a"), initializer),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_uninitialized_access_deep_inside_nested_for_and_if(self):
        statements = [
            VarStmt(token("count")),
            ForStmt(
                initializer=VarStmt(token("i"), LiteralExpr(0)),
                condition=BinaryExpr(
                    VariableExpr(token("i")), token("<"), LiteralExpr(10)
                ),
                increment=AssignExpr(
                    token("i"),
                    BinaryExpr(VariableExpr(token("i")), token("+"), LiteralExpr(1)),
                ),
                body=BlockStmt(
                    [
                        IfStmt(
                            condition=BinaryExpr(
                                VariableExpr(token("i")), token("=="), LiteralExpr(5)
                            ),
                            then_branch=BlockStmt(
                                [
                                    ExpressionStmt(VariableExpr(token("count"))),
                                ]
                            ),
                        ),
                    ]
                ),
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
            VarStmt(token("shared"), LiteralExpr(1)),
            IfStmt(
                condition=VariableExpr(token("shared")),
                then_branch=BlockStmt(
                    [
                        VarStmt(token("dup"), LiteralExpr(1)),
                        VarStmt(token("dup"), LiteralExpr(2)),
                    ]
                ),
                else_branch=BlockStmt(
                    [
                        VarStmt(token("u")),
                        ExpressionStmt(VariableExpr(token("u"))),
                    ]
                ),
            ),
            ForStmt(
                initializer=VarStmt(token("k"), VariableExpr(token("k"))),
                condition=None,
                increment=None,
                body=BlockStmt(
                    [
                        ExpressionStmt(VariableExpr(token("shared"))),
                    ]
                ),
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
                then_branch=BlockStmt(
                    [
                        VarStmt(token("dup"), LiteralExpr(1)),
                        VarStmt(token("dup"), LiteralExpr(2)),
                    ]
                ),
                else_branch=BlockStmt(
                    [
                        VarStmt(token("ok"), LiteralExpr(1)),
                        ExpressionStmt(VariableExpr(token("ok"))),
                    ]
                ),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "dup" in errors[0]


class TestStmtFlowSensitivity:
    def test_else_branch_still_uninitialized_when_only_then_branch_assigns(self):
        # var a;
        # if ( False ) { a = 1; } else { print a; }
        #
        # then_branch 에서 a 를 초기화하더라도, 실제 실행 시 else_branch 를 타면
        # a 는 여전히 미초기화 상태다. 두 분기는 서로 배타적인 실행 경로이므로
        # 한쪽 분기의 초기화가 다른 쪽 분기에 영향을 주면 안 된다.
        statements = [
            VarStmt(token("a")),
            IfStmt(
                condition=LiteralExpr(False),
                then_branch=BlockStmt(
                    [
                        ExpressionStmt(AssignExpr(token("a"), LiteralExpr(1))),
                    ]
                ),
                else_branch=BlockStmt(
                    [
                        ExpressionStmt(VariableExpr(token("a"))),
                    ]
                ),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_uninitialized_access_after_loop_body_never_runs(self):
        # var a;
        # for (; false; ) { a = 1; }
        # print a;
        #
        # condition 이 항상 false 이므로 body 는 한 번도 실행되지 않는다.
        # body 안에서만 초기화되는 변수를 반복문 이후에 읽으면 여전히
        # 미초기화 오류여야 한다.
        statements = [
            VarStmt(token("a")),
            ForStmt(
                initializer=None,
                condition=LiteralExpr(False),
                increment=None,
                body=BlockStmt(
                    [
                        ExpressionStmt(AssignExpr(token("a"), LiteralExpr(1))),
                    ]
                ),
            ),
            ExpressionStmt(VariableExpr(token("a"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_increment_does_not_hide_uninitialized_read_in_first_iteration(self):
        # var x;
        # for (var i = 0; i < 3; x = 1) { print x; }
        #
        # 실제 실행 순서는 condition -> body -> increment 이므로, 첫 반복에서
        # body 가 실행될 때 x 는 아직 increment 로 초기화되기 전이다.
        statements = [
            VarStmt(token("x")),
            ForStmt(
                initializer=VarStmt(token("i"), LiteralExpr(0)),
                condition=BinaryExpr(
                    VariableExpr(token("i")), token("<"), LiteralExpr(3)
                ),
                increment=AssignExpr(token("x"), LiteralExpr(1)),
                body=BlockStmt(
                    [
                        ExpressionStmt(VariableExpr(token("x"))),
                    ]
                ),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "x" in errors[0]


class TestCheckPerformsConstantFolding:
    def test_check_folds_constant_subexpression_in_place(self):
        # var a = 2 + 3;
        # check() 를 호출하고 나면, 호출부가 들고 있는 statements 트리 자체가
        # 이미 상수 폴딩된 상태여야 한다 (Checker.check() 가 내부적으로
        # ConstantFolder 를 먼저 돌리고, 그 결과로 검사를 수행하기 때문).
        plus = Token(TokenType.PLUS, "+")
        initializer = BinaryExpr(LiteralExpr(2), plus, LiteralExpr(3))
        statements = [
            VarStmt(token("a"), initializer),
        ]

        errors = check(statements)

        assert errors == []
        assert isinstance(statements[0].initializer, LiteralExpr)
        assert statements[0].initializer.value == 5

    def test_check_still_reports_errors_using_the_folded_tree(self):
        # var a = a + (2 + 3);
        # 자기 참조 검사는 상수 폴딩 이후에도 정확히 동작해야 한다: 안쪽의
        # (2 + 3) 은 5 로 접히더라도, 바깥의 VariableExpr(a) 는 그대로 남아
        # 자기 참조 오류가 검출돼야 한다.
        plus = Token(TokenType.PLUS, "+")
        initializer = BinaryExpr(
            VariableExpr(token("a")),
            plus,
            BinaryExpr(LiteralExpr(2), plus, LiteralExpr(3)),
        )
        statements = [
            VarStmt(token("a"), initializer),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]
        assert isinstance(statements[0].initializer.right, LiteralExpr)
        assert statements[0].initializer.right.value == 5

    def test_division_by_zero_constant_is_left_for_runtime_to_reject(self):
        # 상수 폴딩이 0으로 나누기를 미리 계산하려다 실패하면, 트리를 그대로
        # 두어 실행 시점에 지금처럼 런타임 오류가 나게 해야 한다. Checker 는
        # 이런 계산 실패를 스스로 오류로 보고하지 않는다 (검사 대상이 아님).
        slash = Token(TokenType.SLASH, "/")
        statements = [
            VarStmt(token("a"), BinaryExpr(LiteralExpr(3), slash, LiteralExpr(0))),
        ]

        errors = check(statements)

        assert errors == []
        assert isinstance(statements[0].initializer, BinaryExpr)


class TestIndexGetExprIsResolved:
    def test_uninitialized_array_variable_is_error(self):
        statements = [
            VarStmt(token("arr")),
            ExpressionStmt(
                IndexGetExpr(VariableExpr(token("arr")), bracket(), LiteralExpr(0))
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "arr" in errors[0]

    def test_uninitialized_index_variable_is_error(self):
        statements = [
            VarStmt(token("arr"), LiteralExpr(0)),
            VarStmt(token("i")),
            ExpressionStmt(
                IndexGetExpr(
                    VariableExpr(token("arr")), bracket(), VariableExpr(token("i"))
                )
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "i" in errors[0]

    def test_self_reference_through_index_get_in_initializer_is_error(self):
        # var arr = arr[0];
        statements = [
            VarStmt(
                token("arr"),
                IndexGetExpr(VariableExpr(token("arr")), bracket(), LiteralExpr(0)),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "arr" in errors[0]

    def test_fully_initialized_index_get_produces_no_error(self):
        statements = [
            VarStmt(token("arr"), LiteralExpr(0)),
            VarStmt(token("i"), LiteralExpr(0)),
            ExpressionStmt(
                IndexGetExpr(
                    VariableExpr(token("arr")), bracket(), VariableExpr(token("i"))
                )
            ),
        ]

        assert check(statements) == []


class TestIndexSetExprIsResolved:
    def test_uninitialized_value_being_assigned_is_error(self):
        # var arr = 0; var x; arr[0] = x;
        statements = [
            VarStmt(token("arr"), LiteralExpr(0)),
            VarStmt(token("x")),
            ExpressionStmt(
                IndexSetExpr(
                    VariableExpr(token("arr")),
                    bracket(),
                    LiteralExpr(0),
                    VariableExpr(token("x")),
                )
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "x" in errors[0]

    def test_uninitialized_array_target_is_error(self):
        statements = [
            VarStmt(token("arr")),
            ExpressionStmt(
                IndexSetExpr(
                    VariableExpr(token("arr")),
                    bracket(),
                    LiteralExpr(0),
                    LiteralExpr(1),
                )
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "arr" in errors[0]

    def test_uninitialized_index_expression_is_error(self):
        statements = [
            VarStmt(token("arr"), LiteralExpr(0)),
            VarStmt(token("i")),
            ExpressionStmt(
                IndexSetExpr(
                    VariableExpr(token("arr")),
                    bracket(),
                    VariableExpr(token("i")),
                    LiteralExpr(1),
                )
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "i" in errors[0]

    def test_self_reference_through_index_set_value_in_initializer_is_error(self):
        # var arr = 0; var x = arr[0] = x;
        statements = [
            VarStmt(token("arr"), LiteralExpr(0)),
            VarStmt(
                token("x"),
                IndexSetExpr(
                    VariableExpr(token("arr")),
                    bracket(),
                    LiteralExpr(0),
                    VariableExpr(token("x")),
                ),
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "x" in errors[0]

    def test_fully_initialized_index_set_produces_no_error(self):
        statements = [
            VarStmt(token("arr"), LiteralExpr(0)),
            VarStmt(token("i"), LiteralExpr(0)),
            ExpressionStmt(
                IndexSetExpr(
                    VariableExpr(token("arr")),
                    bracket(),
                    VariableExpr(token("i")),
                    LiteralExpr(1),
                )
            ),
        ]

        assert check(statements) == []
