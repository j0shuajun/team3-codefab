"""클래스 관련 의미 오류 검사 테스트.

1. 클래스 외부에서 This 사용
2. init 에서 값이 있는 return 사용
3. 자기 자신을 상속
4. 클래스 외부에서 Super 사용
5. 부모(superclass) 없는 클래스에서 Super 사용
"""

from assembler.expr import (
    CallExpr,
    GetExpr,
    LiteralExpr,
    SuperExpr,
    ThisExpr,
    VariableExpr,
)
from assembler.statement import ClassStmt, ExpressionStmt, FunctionStmt, ReturnStmt
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
                        [ExpressionStmt(GetExpr(ThisExpr(token("This")), token("name")))],
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

    def test_super_call_in_subclass_is_allowed(self):
        statements = [
            ClassStmt(token("Base"), [method("greet", [])]),
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
                superclass=VariableExpr(token("Base")),
            ),
        ]

        assert check(statements) == []
