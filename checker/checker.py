from checker.error_reporter import ErrorReporter
from checker.resolver import ExpressionResolver, StatementResolver
from checker.scope_stack import ScopeStack


class Checker:
    def __init__(self):
        self._scopes = ScopeStack()
        self._error_reporter = ErrorReporter()
        self._expression_resolver = ExpressionResolver(
            self._scopes, self._error_reporter
        )
        self._statement_resolver = StatementResolver(
            self._scopes, self._error_reporter, self._expression_resolver
        )

    def check(self, statements):
        self._scopes.reset()
        self._error_reporter.reset()
        self._statement_resolver.resolve_all(statements)
        return self._error_reporter.errors
