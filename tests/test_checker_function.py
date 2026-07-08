"""함수 관련 의미 오류 검사 테스트.

1. 함수 외부(top-level code)에서 return 사용 검출
2. 함수 파라미터 이름 중복 검출
"""

from assembler.expr import LiteralExpr, VariableExpr
from assembler.statement import (
    BlockStmt,
    ExpressionStmt,
    FunctionStmt,
    ReturnStmt,
    VarStmt,
)
from assembler.tokenizer import Token, TokenType
from checker.checker import Checker


def token(origin):
    return Token(TokenType.IDENTIFIER, origin)


def check(statements):
    return Checker().check(statements)


class TestReturnOutsideFunction:
    def test_top_level_return_with_value_is_error(self):
        statements = [
            ReturnStmt(token("return"), LiteralExpr(1)),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "return" in errors[0].lower()

    def test_top_level_return_without_value_is_error(self):
        statements = [
            ReturnStmt(token("return")),
        ]

        errors = check(statements)

        assert len(errors) == 1

    def test_return_inside_block_but_outside_function_is_error(self):
        statements = [
            BlockStmt(
                [
                    ReturnStmt(token("return"), LiteralExpr(1)),
                ]
            ),
        ]

        errors = check(statements)

        assert len(errors) == 1

    def test_return_inside_function_is_allowed(self):
        statements = [
            FunctionStmt(
                token("f"),
                [],
                [ReturnStmt(token("return"), LiteralExpr(1))],
            ),
        ]

        assert check(statements) == []

    def test_return_without_value_inside_function_is_allowed(self):
        statements = [
            FunctionStmt(
                token("f"),
                [],
                [ReturnStmt(token("return"))],
            ),
        ]

        assert check(statements) == []

    def test_return_inside_nested_block_within_function_is_allowed(self):
        statements = [
            FunctionStmt(
                token("f"),
                [],
                [BlockStmt([ReturnStmt(token("return"), LiteralExpr(1))])],
            ),
        ]

        assert check(statements) == []

    def test_return_after_function_body_at_top_level_is_still_error(self):
        # 함수 본문 안에서는 허용되지만, 함수가 끝난 뒤 같은 스코프의 return 은
        # 여전히 함수 바깥 코드이므로 오류여야 한다.
        statements = [
            FunctionStmt(
                token("f"),
                [],
                [ReturnStmt(token("return"), LiteralExpr(1))],
            ),
            ReturnStmt(token("return"), LiteralExpr(2)),
        ]

        errors = check(statements)

        assert len(errors) == 1

    def test_return_value_expression_is_still_resolved(self):
        # 함수 바깥의 return 이라도, return 값 표현식 자체는 계속 검사돼야 한다
        # (여기서는 자기 참조 없는 정상 케이스로, 오류가 return 오류 하나만 나야 함).
        statements = [
            VarStmt(token("a"), LiteralExpr(1)),
            ReturnStmt(token("return"), VariableExpr(token("a"))),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "return" in errors[0].lower()


class TestDuplicateParameterNames:
    def test_duplicate_parameter_names_is_error(self):
        statements = [
            FunctionStmt(token("f"), [token("a"), token("a")], []),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_three_parameters_with_one_duplicate_reports_single_error(self):
        statements = [
            FunctionStmt(token("f"), [token("a"), token("b"), token("a")], []),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "a" in errors[0]

    def test_unique_parameter_names_is_allowed(self):
        statements = [
            FunctionStmt(token("f"), [token("a"), token("b")], []),
        ]

        assert check(statements) == []

    def test_no_parameters_is_allowed(self):
        statements = [
            FunctionStmt(token("f"), [], []),
        ]

        assert check(statements) == []

    def test_parameter_usable_inside_function_body_without_uninitialized_error(self):
        statements = [
            FunctionStmt(
                token("f"),
                [token("a")],
                [ExpressionStmt(VariableExpr(token("a")))],
            ),
        ]

        assert check(statements) == []

    def test_duplicate_function_declaration_is_error_like_variables(self):
        # 함수 이름도 일반 선언과 같은 스코프 메커니즘을 타므로, 같은 스코프에
        # 같은 이름의 함수가 두 번 선언되면 중복 선언 오류가 나야 한다.
        statements = [
            FunctionStmt(token("f"), [], []),
            FunctionStmt(token("f"), [], []),
        ]

        errors = check(statements)

        assert len(errors) == 1
        assert "f" in errors[0]
