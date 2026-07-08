from assembler.expr import (
    AssignExpr,
    BinaryExpr,
    Expr,
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
    Stmt,
    VarStmt,
)

from exceptions import CodeFabRuntimeError, CodeFabTypeError
from executor.executor import Executor


class ConstantFolder:
    """실행 전에 리터럴로만 이루어진 부분식을 미리 계산해 LiteralExpr 로 치환한다.

    변수가 하나라도 섞여 있는 서브트리는 절대 접지 않는다. 계산 도중 런타임 오류
    (0으로 나누기, 타입 불일치 등)가 나면 최적화를 포기하고 원본을 그대로 둬서,
    실행 시점에 지금과 동일한 오류가 나도록 한다. 연산 규칙은 Executor.evaluate() 를
    그대로 재사용해서, 최적화 전/후 결과가 어긋날 여지를 없앤다.
    """

    def __init__(self):
        self._executor = Executor()
        self._statement_folders = {
            VarStmt: self._fold_var_stmt,
            BlockStmt: self._fold_block_stmt,
            ExpressionStmt: self._fold_expression_stmt,
            PrintStmt: self._fold_expression_stmt,
            IfStmt: self._fold_if_stmt,
            ForStmt: self._fold_for_stmt,
        }
        self._expr_folders = {
            LiteralExpr: self._fold_literal_expr,
            VariableExpr: self._fold_variable_expr,
            AssignExpr: self._fold_assign_expr,
            BinaryExpr: self._fold_binary_expr,
            LogicalExpr: self._fold_logical_expr,
            UnaryExpr: self._fold_unary_expr,
            GroupingExpr: self._fold_grouping_expr,
        }

    def fold(self, statements):
        return [self._fold_statement(statement) for statement in statements]

    def _fold_statement(self, statement):
        folder = self._statement_folders.get(type(statement))
        if folder is not None:
            return folder(statement)

        if not isinstance(statement, Stmt):
            raise CodeFabTypeError(f"Unknown statement type: {type(statement).__name__}")
        return statement

    def _fold_expr(self, expr):
        folder = self._expr_folders.get(type(expr))
        if folder is not None:
            return folder(expr)

        if not isinstance(expr, Expr):
            raise CodeFabTypeError(f"Unknown expression type: {type(expr).__name__}")
        return expr

    # --- statement folders -------------------------------------------------

    def _fold_var_stmt(self, statement):
        if statement.initializer is not None:
            statement.initializer = self._fold_expr(statement.initializer)
        return statement

    def _fold_block_stmt(self, statement):
        statement.statements = self.fold(statement.statements)
        return statement

    def _fold_expression_stmt(self, statement):
        statement.expression = self._fold_expr(statement.expression)
        return statement

    def _fold_if_stmt(self, statement):
        statement.condition = self._fold_expr(statement.condition)
        statement.then_branch = self._fold_statement(statement.then_branch)
        if statement.else_branch is not None:
            statement.else_branch = self._fold_statement(statement.else_branch)
        return statement

    def _fold_for_stmt(self, statement):
        if statement.initializer is not None:
            statement.initializer = self._fold_statement(statement.initializer)
        if statement.condition is not None:
            statement.condition = self._fold_expr(statement.condition)
        if statement.increment is not None:
            statement.increment = self._fold_expr(statement.increment)
        statement.body = self._fold_statement(statement.body)
        return statement

    # --- expression folders -------------------------------------------------

    def _fold_literal_expr(self, expr):
        return expr

    def _fold_variable_expr(self, expr):
        return expr

    def _fold_assign_expr(self, expr):
        # 대입은 항상 부작용(환경에 값 저장)이 있으므로 노드 자체는 절대 리터럴로
        # 치환하지 않는다. 대입되는 값만 접는다.
        expr.value = self._fold_expr(expr.value)
        return expr

    def _fold_binary_expr(self, expr):
        expr.left = self._fold_expr(expr.left)
        expr.right = self._fold_expr(expr.right)
        return self._try_fold(expr)

    def _fold_logical_expr(self, expr):
        expr.left = self._fold_expr(expr.left)
        expr.right = self._fold_expr(expr.right)
        return self._try_fold(expr)

    def _fold_unary_expr(self, expr):
        expr.right = self._fold_expr(expr.right)
        return self._try_fold(expr)

    def _fold_grouping_expr(self, expr):
        expr.expression = self._fold_expr(expr.expression)
        if isinstance(expr.expression, LiteralExpr):
            return expr.expression
        return expr

    def _try_fold(self, expr):
        if not self._all_operands_are_literal(expr):
            return expr

        try:
            value = self._executor.evaluate(expr)
        except CodeFabRuntimeError:
            # 런타임에도 똑같이 실패해야 하므로 최적화를 포기하고 원본을 남긴다.
            return expr

        return LiteralExpr(value)

    @staticmethod
    def _all_operands_are_literal(expr):
        if isinstance(expr, UnaryExpr):
            return isinstance(expr.right, LiteralExpr)
        return isinstance(expr.left, LiteralExpr) and isinstance(expr.right, LiteralExpr)
