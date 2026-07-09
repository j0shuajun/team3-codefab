"""클래스 관련 의미 오류 검사 테스트.

1. 클래스 외부에서 This 사용
2. init 안에서의 return 사용
3. 자기 자신을 상속
4. 클래스 외부에서 Super 사용
5. 부모(superclass) 없는 클래스에서 Super 사용

추가 검증 목록.
- 메서드 본문 resolve 가 바깥 스코프의 초기화 상태를 오염시키는지 (false negative)
- 잘못된 미초기화 오류를 내지 않는지 (false positive)
"""

from assembler.expr import (
    AssignExpr,
    CallExpr,
    GetExpr,
    LiteralExpr,
    SetExpr,
    SuperExpr,
    ThisExpr,
    VariableExpr,
)
from assembler.statement import (
    ClassStmt,
    ExpressionStmt,
    FunctionStmt,
    ReturnStmt,
    VarStmt,
)
from assembler.tokenizer import Token, TokenType
from checker.checker import Checker


def token(origin):
    return Token(TokenType.IDENTIFIER, origin)


def method(name, body, params=None):
    return FunctionStmt(token(name), params or [], body)


def check(statements):
    return Checker().check(statements)


class TestThisOutsideClass:
    def test_top_level_this_is_error(self):
        statements = [
            ExpressionStmt(ThisExpr(token("This"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "this" in errors[0].lower()

    def test_this_inside_plain_function_is_still_error(self):
        # This 는 클래스 메서드 안에서만 허용되고, 일반 함수 안에서는 여전히 오류다.
        statements = [
            FunctionStmt(token("f"), [], [ExpressionStmt(ThisExpr(token("This")))]),
        ]

        errors = check(statements)

        assert len(errors) == 1

    def test_this_inside_method_is_allowed(self):
        statements = [
            ClassStmt(
                token("A"),
                [method("greet", [ExpressionStmt(ThisExpr(token("This")))])],
            ),
        ]

        assert check(statements) == []

    def test_this_field_access_inside_method_is_allowed(self):
        # This.name 처럼 GetExpr 에 감싸여 있어도 검사가 통과해야 한다.
        statements = [
            ClassStmt(
                token("A"),
                [
                    method(
                        "greet",
                        [
                            ExpressionStmt(
                                GetExpr(ThisExpr(token("This")), token("name"))
                            )
                        ],
                    )
                ],
            ),
        ]

        assert check(statements) == []

    def test_this_field_access_outside_class_is_error(self):
        statements = [
            ExpressionStmt(GetExpr(ThisExpr(token("This")), token("name"))),
        ]

        errors = check(statements)

        assert len(errors) == 1

    def test_this_field_set_inside_method_is_allowed(self):
        # This.name = value; 형태 (SetExpr) 도 object/value 가 재귀 resolve 돼야 한다.
        statements = [
            ClassStmt(
                token("A"),
                [
                    method(
                        "init",
                        [
                            ExpressionStmt(
                                SetExpr(
                                    ThisExpr(token("This")),
                                    token("name"),
                                    LiteralExpr("codefab"),
                                )
                            )
                        ],
                        params=[token("name")],
                    )
                ],
            ),
        ]

        assert check(statements) == []


class TestReturnInsideInitializer:
    def test_return_with_value_in_init_is_error(self):
        statements = [
            ClassStmt(
                token("A"),
                [method("init", [ReturnStmt(token("return"), LiteralExpr(5))])],
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "initializer" in errors[0].lower()

    def test_bare_return_in_init_is_also_error(self):
        # 값이 없는 return 이라도 init 안에서는 return 문 자체가 허용되지 않는다.
        statements = [
            ClassStmt(
                token("A"),
                [method("init", [ReturnStmt(token("return"))])],
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "initializer" in errors[0].lower()

    def test_return_with_value_in_regular_method_is_allowed(self):
        statements = [
            ClassStmt(
                token("A"),
                [method("greet", [ReturnStmt(token("return"), LiteralExpr(5))])],
            ),
        ]

        assert check(statements) == []

    def test_bare_return_in_regular_method_is_allowed(self):
        statements = [
            ClassStmt(
                token("A"),
                [method("greet", [ReturnStmt(token("return"))])],
            ),
        ]

        assert check(statements) == []


class TestClassInheritingItself:
    def test_class_inheriting_itself_is_error(self):
        statements = [
            ClassStmt(token("A"), [], superclass=VariableExpr(token("A"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "itself" in errors[0].lower()

    def test_class_inheriting_another_class_is_allowed(self):
        statements = [
            ClassStmt(token("Base"), []),
            ClassStmt(token("A"), [], superclass=VariableExpr(token("Base"))),
        ]

        assert check(statements) == []

    def test_class_without_superclass_is_allowed(self):
        statements = [
            ClassStmt(token("A"), []),
        ]

        assert check(statements) == []

    def test_duplicate_class_declaration_is_error(self):
        statements = [
            ClassStmt(token("A"), []),
            ClassStmt(token("A"), []),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0].lower()


class TestSuperOutsideClass:
    def test_top_level_super_call_is_error(self):
        statements = [
            ExpressionStmt(
                CallExpr(SuperExpr(token("Super"), token("greet")), token(")"), [])
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "super" in errors[0].lower()

    def test_super_inside_plain_function_is_still_error(self):
        statements = [
            FunctionStmt(
                token("f"),
                [],
                [
                    ExpressionStmt(
                        CallExpr(
                            SuperExpr(token("Super"), token("greet")), token(")"), []
                        )
                    )
                ],
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1


class TestSuperWithoutSuperclass:
    def test_super_call_in_class_without_superclass_is_error(self):
        statements = [
            ClassStmt(
                token("A"),
                [
                    method(
                        "greet",
                        [
                            ExpressionStmt(
                                CallExpr(
                                    SuperExpr(token("Super"), token("greet")),
                                    token(")"),
                                    [],
                                )
                            )
                        ],
                    )
                ],
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "superclass" in errors[0].lower()

    def test_super_call_with_arguments_in_subclass_is_allowed(self):
        # CallExpr 의 arguments 순회 경로까지 실제로 태우는 케이스.
        statements = [
            ClassStmt(token("Base"), [method("greet", [], params=[token("name")])]),
            ClassStmt(
                token("A"),
                [
                    method(
                        "greet",
                        [
                            ExpressionStmt(
                                CallExpr(
                                    SuperExpr(token("Super"), token("greet")),
                                    token(")"),
                                    [LiteralExpr("codefab")],
                                )
                            )
                        ],
                        params=[token("name")],
                    )
                ],
                superclass=VariableExpr(token("Base")),
            ),
        ]

        assert check(statements) == []


class TestMethodBodyScopeIsolation:
    """메서드/함수 본문 resolve 가 바깥 스코프의 초기화 상태를
    선언 시점에 오염시키면 안 된다 (읽기/쓰기 양방향)."""

    def test_assignment_inside_method_does_not_leak_initialization_to_outer_scope(self):
        # Class A { method() { x = 1; } }
        # var x;
        # print x;
        #
        # method() 는 호출된 적이 없으므로, x 는 여전히 미초기화 상태여야 한다.
        statements = [
            ClassStmt(
                token("A"),
                [
                    method(
                        "method",
                        [ExpressionStmt(AssignExpr(token("x"), LiteralExpr(1)))],
                    )
                ],
            ),
            VarStmt(token("x")),
            ExpressionStmt(VariableExpr(token("x"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "x" in errors[0]

    def test_assignment_inside_plain_function_does_not_leak_initialization(self):
        # 클래스 메서드뿐 아니라 일반 함수도 동일하게 격리돼야 한다.
        statements = [
            FunctionStmt(
                token("f"),
                [],
                [ExpressionStmt(AssignExpr(token("x"), LiteralExpr(1)))],
            ),
            VarStmt(token("x")),
            ExpressionStmt(VariableExpr(token("x"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "x" in errors[0]

    def test_method_reading_outer_variable_initialized_after_declaration_is_allowed(
        self,
    ):
        # var x;
        # Class A { method() { print x; } }
        # x = 5;
        #
        # method() 는 나중에 호출될 것이므로, 지금 이 시점에 x 가 아직 미초기화라는
        # 사실만으로 오류를 내면 안 된다 (거짓 양성).
        statements = [
            VarStmt(token("x")),
            ClassStmt(
                token("A"),
                [method("method", [ExpressionStmt(VariableExpr(token("x")))])],
            ),
            ExpressionStmt(AssignExpr(token("x"), LiteralExpr(5))),
        ]

        assert check(statements) == []

    def test_function_reading_outer_variable_initialized_after_declaration_is_allowed(
        self,
    ):
        statements = [
            VarStmt(token("x")),
            FunctionStmt(
                token("f"),
                [],
                [ExpressionStmt(VariableExpr(token("x")))],
            ),
            ExpressionStmt(AssignExpr(token("x"), LiteralExpr(5))),
        ]

        assert check(statements) == []

    def test_real_uninitialized_access_outside_any_function_is_still_caught(self):
        # 격리 로직이 함수/메서드 밖의 정상적인 미초기화 검사에 영향을 주면 안 된다.
        statements = [
            VarStmt(token("y")),
            ExpressionStmt(VariableExpr(token("y"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "y" in errors[0]

    def test_self_reference_inside_method_own_local_is_still_caught(self):
        # 바깥 스코프는 격리 대상이지만, 메서드 자기 자신의 로컬 변수에 대한
        # 자기 참조/미초기화 검사는 여전히 엄격하게 적용돼야 한다.
        statements = [
            ClassStmt(
                token("A"),
                [
                    method(
                        "method",
                        [VarStmt(token("local"), VariableExpr(token("local")))],
                    )
                ],
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "local" in errors[0]

    def test_uninitialized_param_is_not_flagged_when_reading_outer_variable(self):
        # 파라미터는 항상 초기화된 것으로 취급되고, 바깥 변수를 읽는 것도
        # (격리 덕분에) 오류가 나지 않아야 한다.
        statements = [
            VarStmt(token("shared")),
            ClassStmt(
                token("A"),
                [
                    method(
                        "method",
                        [
                            ExpressionStmt(VariableExpr(token("value"))),
                            ExpressionStmt(VariableExpr(token("shared"))),
                        ],
                        params=[token("value")],
                    )
                ],
            ),
        ]

        assert check(statements) == []
