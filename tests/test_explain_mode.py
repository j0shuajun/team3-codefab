from shell.explain_mode import ExplainMode


def test_explain_shows_tokens_ast_checker_and_result():
    outputs = ExplainMode().explain_source("var x = 1 + 2 * 3;")

    assert "[Tokens]" in outputs
    assert (
        "VAR IDENTIFIER EQUAL NUMBER PLUS NUMBER STAR NUMBER SEMICOLON EOF" in outputs
    )

    assert "[AST]" in outputs
    assert any("VarStmt" in output for output in outputs)

    assert "[Checker]" in outputs
    assert "No errors" in outputs

    assert "[Result]" in outputs
    assert "[Variables]" in outputs
    assert "x = 7" in outputs


def test_explain_shows_print_output():
    outputs = ExplainMode().explain_source("print 1 + 2 * 3;")

    assert "[Result]" in outputs
    assert "[Output]" in outputs
    assert "7" in outputs


def test_explain_returns_checker_errors():
    outputs = ExplainMode().explain_source("var a = a;")

    assert "[Checker]" in outputs
    assert any("a" in output for output in outputs)
    assert "[Result]" not in outputs
