"""상수 연산 최적화(constant folding) 테스트.

1. ConstantFolder 가 리터럴로만 이루어진 부분식을 실제로 LiteralExpr 로 치환하는지
   (트리 모양에 대한 순수한 assertion)
2. 변수가 섞여 있거나 계산 중 런타임 오류가 나는 식은 절대 접지 않는지
3. 최적화 이후 실행 시 해당 부분식에 대한 연산 횟수가 실제로 줄어드는지
   (Test Double 로 연산 호출 횟수 검증)
"""

from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from assembler.statement import (
    BlockStmt,
    ExpressionStmt,
    ForStmt,
    IfStmt,
    PrintStmt,
    VarStmt,
)
from assembler.tokenizer import Token, TokenType
from checker.constant_folder import ConstantFolder
from exceptions import CodeFabRuntimeError
from executor.executor import Executor


def token(origin, token_type=TokenType.IDENTIFIER):
    return Token(token_type, origin)


def op(origin, token_type):
    return Token(token_type, origin)


def fold_expr(expr):
    """단일 Expr 를 접어서 결과를 돌려주는 테스트 헬퍼."""
    statement = ExpressionStmt(expr)
    ConstantFolder().fold([statement])
    return statement.expression


class TestFoldsPureLiteralSubexpressions:
    def test_binary_expr_of_two_literals_is_folded(self):
        expr = BinaryExpr(LiteralExpr(2), op("+", TokenType.PLUS), LiteralExpr(3))

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value == 5

    def test_nested_binary_expr_is_folded_into_single_literal(self):
        # (2 + 3) * 4
        expr = BinaryExpr(
            GroupingExpr(
                BinaryExpr(LiteralExpr(2), op("+", TokenType.PLUS), LiteralExpr(3))
            ),
            op("*", TokenType.STAR),
            LiteralExpr(4),
        )

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value == 20

    def test_long_chain_of_constant_operations_folds_to_single_literal(self):
        # 1 - 2*3*4*5/6 + 7 + 8 + 9
        def lit(value):
            return LiteralExpr(value)

        product = BinaryExpr(
            BinaryExpr(
                BinaryExpr(lit(2), op("*", TokenType.STAR), lit(3)),
                op("*", TokenType.STAR),
                lit(4),
            ),
            op("*", TokenType.STAR),
            lit(5),
        )
        division = BinaryExpr(product, op("/", TokenType.SLASH), lit(6))
        subtraction = BinaryExpr(lit(1), op("-", TokenType.MINUS), division)
        plus_seven = BinaryExpr(subtraction, op("+", TokenType.PLUS), lit(7))
        plus_eight = BinaryExpr(plus_seven, op("+", TokenType.PLUS), lit(8))
        expr = BinaryExpr(plus_eight, op("+", TokenType.PLUS), lit(9))

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value == 1 - 2 * 3 * 4 * 5 / 6 + 7 + 8 + 9

    def test_unary_minus_of_literal_is_folded(self):
        expr = UnaryExpr(op("-", TokenType.MINUS), LiteralExpr(5))

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value == -5

    def test_unary_bang_of_literal_is_folded(self):
        expr = UnaryExpr(op("!", TokenType.BANG), LiteralExpr(True))

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value is False

    def test_grouping_of_literal_is_unwrapped_to_literal(self):
        expr = GroupingExpr(LiteralExpr(42))

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value == 42

    def test_logical_and_of_two_literals_is_folded(self):
        expr = LogicalExpr(
            LiteralExpr(False), op("and", TokenType.AND), LiteralExpr(True)
        )

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value is False

    def test_logical_or_of_two_literals_is_folded(self):
        expr = LogicalExpr(
            LiteralExpr(False), op("or", TokenType.OR), LiteralExpr(True)
        )

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value is True


class TestDoesNotFoldNonConstantOrUnsafeExpressions:
    def test_binary_expr_with_variable_operand_is_left_untouched(self):
        expr = BinaryExpr(
            VariableExpr(token("a")), op("+", TokenType.PLUS), LiteralExpr(1)
        )

        folded = fold_expr(expr)

        assert folded is expr
        assert isinstance(folded, BinaryExpr)

    def test_constant_subexpression_inside_larger_expression_is_still_folded(self):
        # a + (2 * 3)  ->  a + 6
        expr = BinaryExpr(
            VariableExpr(token("a")),
            op("+", TokenType.PLUS),
            BinaryExpr(LiteralExpr(2), op("*", TokenType.STAR), LiteralExpr(3)),
        )

        folded = fold_expr(expr)

        assert isinstance(folded, BinaryExpr)
        assert isinstance(folded.right, LiteralExpr)
        assert folded.right.value == 6

    def test_division_by_zero_is_not_folded(self):
        expr = BinaryExpr(LiteralExpr(3), op("/", TokenType.SLASH), LiteralExpr(0))

        folded = fold_expr(expr)

        assert folded is expr
        assert isinstance(folded, BinaryExpr)

        # 접지 않았으니 실행 시점엔 지금과 동일하게 런타임 오류가 나야 한다.
        try:
            Executor().evaluate(folded)
            assert False, "should have raised CodeFabRuntimeError"
        except CodeFabRuntimeError:
            pass

    def test_type_mismatch_is_not_folded(self):
        expr = BinaryExpr(LiteralExpr(3), op(">", TokenType.GREATER), LiteralExpr("a"))

        folded = fold_expr(expr)

        assert folded is expr

    def test_assign_expr_itself_is_never_replaced_only_its_value(self):
        assign = AssignExpr(
            token("a"),
            BinaryExpr(LiteralExpr(2), op("+", TokenType.PLUS), LiteralExpr(3)),
        )

        folded = fold_expr(assign)

        assert folded is assign
        assert isinstance(folded.value, LiteralExpr)
        assert folded.value.value == 5

    def test_variable_expr_is_left_untouched(self):
        variable = VariableExpr(token("a"))

        folded = fold_expr(variable)

        assert folded is variable


class TestFoldsThroughStatementTree:
    def test_var_stmt_initializer_is_folded(self):
        statements = [
            VarStmt(
                token("a"),
                BinaryExpr(LiteralExpr(2), op("+", TokenType.PLUS), LiteralExpr(3)),
            ),
        ]

        ConstantFolder().fold(statements)

        assert isinstance(statements[0].initializer, LiteralExpr)
        assert statements[0].initializer.value == 5

    def test_folds_inside_nested_block(self):
        inner_expr = BinaryExpr(LiteralExpr(2), op("+", TokenType.PLUS), LiteralExpr(3))
        statements = [
            BlockStmt(
                [
                    PrintStmt(inner_expr),
                ]
            ),
        ]

        ConstantFolder().fold(statements)

        printed = statements[0].statements[0].expression
        assert isinstance(printed, LiteralExpr)
        assert printed.value == 5

    def test_folds_if_condition_and_branches(self):
        statements = [
            IfStmt(
                condition=BinaryExpr(
                    LiteralExpr(1), op("<", TokenType.LESS), LiteralExpr(2)
                ),
                then_branch=PrintStmt(
                    BinaryExpr(LiteralExpr(2), op("*", TokenType.STAR), LiteralExpr(3))
                ),
                else_branch=PrintStmt(
                    BinaryExpr(LiteralExpr(4), op("*", TokenType.STAR), LiteralExpr(5))
                ),
            ),
        ]

        ConstantFolder().fold(statements)

        stmt = statements[0]
        assert isinstance(stmt.condition, LiteralExpr)
        assert stmt.condition.value is True
        assert stmt.then_branch.expression.value == 6
        assert stmt.else_branch.expression.value == 20

    def test_folds_for_condition_and_increment_but_keeps_loop_variable_dynamic(self):
        statements = [
            ForStmt(
                initializer=VarStmt(token("i"), LiteralExpr(0)),
                condition=BinaryExpr(
                    VariableExpr(token("i")), op("<", TokenType.LESS), LiteralExpr(3)
                ),
                increment=AssignExpr(
                    token("i"),
                    BinaryExpr(
                        VariableExpr(token("i")),
                        op("+", TokenType.PLUS),
                        LiteralExpr(1),
                    ),
                ),
                body=BlockStmt(
                    [
                        PrintStmt(
                            BinaryExpr(
                                LiteralExpr(2), op("+", TokenType.PLUS), LiteralExpr(3)
                            )
                        ),
                    ]
                ),
            ),
        ]

        ConstantFolder().fold(statements)

        for_stmt = statements[0]
        # i 가 껴 있는 condition/increment 는 그대로 남아 있어야 한다.
        assert isinstance(for_stmt.condition, BinaryExpr)
        assert isinstance(for_stmt.increment, AssignExpr)
        assert isinstance(for_stmt.increment.value, BinaryExpr)
        # 순수 상수인 body 안의 print 인자는 접혀야 한다.
        printed = for_stmt.body.statements[0].expression
        assert isinstance(printed, LiteralExpr)
        assert printed.value == 5


class CountingExecutor(Executor):
    """Environment 접근이 아니라 '연산 자체가 몇 번 수행됐는지'를 세는 Test Double."""

    def __init__(self):
        super().__init__()
        self.binary_eval_count = 0

    def evaluate_binary(self, expr):
        self.binary_eval_count += 1
        return super().evaluate_binary(expr)


def make_loop_printing_constant_expression():
    # for (var i = 0; i < 3; i = i + 1) { print (2 + 3) * 4; }
    return [
        ForStmt(
            initializer=VarStmt(token("i"), LiteralExpr(0)),
            condition=BinaryExpr(
                VariableExpr(token("i")), op("<", TokenType.LESS), LiteralExpr(3)
            ),
            increment=AssignExpr(
                token("i"),
                BinaryExpr(
                    VariableExpr(token("i")), op("+", TokenType.PLUS), LiteralExpr(1)
                ),
            ),
            body=BlockStmt(
                [
                    PrintStmt(
                        BinaryExpr(
                            GroupingExpr(
                                BinaryExpr(
                                    LiteralExpr(2),
                                    op("+", TokenType.PLUS),
                                    LiteralExpr(3),
                                )
                            ),
                            op("*", TokenType.STAR),
                            LiteralExpr(4),
                        )
                    ),
                ]
            ),
        ),
    ]


class TestOptimizationReducesRuntimeOperationCount:
    def test_folded_program_performs_fewer_binary_evaluations_at_runtime(self):
        unfolded = make_loop_printing_constant_expression()
        before = CountingExecutor()
        before.execute(unfolded)

        folded = ConstantFolder().fold(make_loop_printing_constant_expression())
        after = CountingExecutor()
        after.execute(folded)

        assert before.outputs == after.outputs == ["20", "20", "20"]

        # 루프 3번을 도는 동안, 상수식 (2 + 3) * 4 에 들어있던 이항연산 2개가
        # 매 반복 실행될 필요가 없어져서 6번(=2 * 3회) 줄어든다.
        # 반면 반복문 제어에 필요한 연산(i < 3, i = i + 1)은 변수를 포함하므로
        # 최적화 전후 동일하게 유지된다.
        assert before.binary_eval_count - after.binary_eval_count == 6

    def test_no_constant_operations_remain_for_fully_literal_expression(self):
        statements = [
            PrintStmt(
                BinaryExpr(
                    GroupingExpr(
                        BinaryExpr(
                            LiteralExpr(2), op("+", TokenType.PLUS), LiteralExpr(3)
                        )
                    ),
                    op("*", TokenType.STAR),
                    LiteralExpr(4),
                )
            ),
        ]

        folded = ConstantFolder().fold(statements)

        executor = CountingExecutor()
        executor.execute(folded)

        assert executor.outputs == ["20"]
        assert executor.binary_eval_count == 0


class TestFoldingSurvivesUnexpectedEvaluationErrors:
    """Executor.evaluate() 가 CodeFabRuntimeError 가 아닌 다른 예외를
    던지는 리터럴 조합(예: 문자열/불리언 비교)에서도 ConstantFolder 가 죽지 않고
    안전하게 원본을 접지 않은 채로 넘겨야 한다."""

    def test_string_equality_of_two_literals_is_folded(self):
        expr = BinaryExpr(
            LiteralExpr("a"), op("==", TokenType.EQUAL_EQUAL), LiteralExpr("a")
        )

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value is True

    def test_boolean_equality_of_two_literals_is_folded(self):
        expr = BinaryExpr(
            LiteralExpr(True), op("==", TokenType.EQUAL_EQUAL), LiteralExpr(True)
        )

        folded = fold_expr(expr)

        assert isinstance(folded, LiteralExpr)
        assert folded.value is True

    def test_mismatched_literal_types_are_not_folded_and_do_not_crash(self):
        expr = BinaryExpr(
            LiteralExpr("a"), op("==", TokenType.EQUAL_EQUAL), LiteralExpr(1)
        )

        folded = fold_expr(expr)

        assert folded is expr
        assert isinstance(folded, BinaryExpr)
