from app.assembler.assembler import Assembler
from app.shell.debug_mode import DebugSession
from app.shell.runner import CodeFabRunner


def make_debug_session(source):
    runner = CodeFabRunner()
    tokens = runner.tokenizer.tokenize(source)
    statements = Assembler(tokens).parse()

    errors = runner.checker.check(statements)
    assert errors == []

    return DebugSession(
        runner,
        statements,
        source_lines=source.splitlines(),
    )


def test_debug_step_executes_current_statement():
    session = make_debug_session("var a = 10;\n" "print a;\n")

    assert session.process_command("step") == ["[DEBUG] 2번째 줄에서 정지 -> print a;"]

    assert session.process_command("step") == [
        "10",
        "[DEBUG] 프로그램 종료",
    ]


def test_debug_watch_prints_variable_after_step():
    session = make_debug_session("var a = 10;\n" "a = a + 5;\n")

    assert session.process_command("watch a") == ["[WATCH] 'a' 감시 등록"]

    assert session.process_command("step") == [
        "[DEBUG] 2번째 줄에서 정지 -> a = a + 5;",
        "[WATCH] a = 10",
    ]

    assert session.process_command("step") == [
        "[DEBUG] 프로그램 종료",
        "[WATCH] a = 15",
    ]


def test_debug_watches_prints_current_watch_values():
    session = make_debug_session("var a = 10;\n")

    session.process_command("watch a")
    session.process_command("step")

    assert session.process_command("watches") == ["[WATCH] a = 10"]


def test_debug_inspect_prints_current_scope_values():
    session = make_debug_session("var a = 10;\n")

    session.process_command("step")

    outputs = session.process_command("inspect")

    assert outputs[0] == "[DEBUG] 현재 scope 변수"
    assert "- a = 10" in outputs


def test_debug_breakpoint_stops_before_line():
    session = make_debug_session("var a = 10;\n" "print a;\n" "print 20;\n")

    assert session.process_command("break 2") == ["[DEBUG] 2번째 줄에 breakpoint 설정"]

    outputs = session.process_command("continue")

    assert outputs == ["[DEBUG] 2번째 줄에서 정지 (breakpoint) -> print a;"]


def test_debug_remove_breakpoint():
    session = make_debug_session("var a = 10;\n" "print a;\n")

    session.process_command("break 2")

    assert session.process_command("remove 2") == ["[DEBUG] 2번째 줄 breakpoint 해제"]

    assert session.process_command("breakpoints") == [
        "[DEBUG] 설정된 breakpoint가 없습니다."
    ]


def test_debug_continue_runs_until_breakpoint():
    session = make_debug_session("var a = 10;\n" "a = a + 5;\n" "print a;\n")

    session.process_command("break 3")

    assert session.process_command("continue") == [
        "[DEBUG] 3번째 줄에서 정지 (breakpoint) -> print a;"
    ]

    assert session.process_command("step") == [
        "15",
        "[DEBUG] 프로그램 종료",
    ]


def test_debug_step_reports_if_condition_error_line():
    session = make_debug_session("if (10 / 0) {\n" "  print 1;\n" "}\n" "print 2;\n")

    outputs = session.process_command("step")

    assert outputs == ["Error at line 1: Division by zero."]


def test_debug_continue_stops_at_breakpoint_inside_for_loop():
    session = make_debug_session(
        "var total = 0;\n"
        "for (var i = 0; i < 3; i = i + 1) {\n"
        "  total = total + i;\n"
        "  print total;\n"
        "}\n"
        'print "done";\n'
    )

    session.process_command("break 4")
    outputs = session.process_command("continue")

    assert outputs == ["[DEBUG] 4번째 줄에서 정지 (breakpoint) -> print total;"]


def test_debug_step_inside_for_loop_executes_only_current_body_statement():
    session = make_debug_session(
        "var total = 0;\n"
        "for (var i = 0; i < 3; i = i + 1) {\n"
        "  total = total + i;\n"
        "  print total;\n"
        "}\n"
        'print "done";\n'
    )

    session.process_command("break 4")
    session.process_command("continue")

    outputs = session.process_command("step")

    assert outputs == [
        "0",
        "[DEBUG] 3번째 줄에서 정지 -> total = total + i;",
    ]


def test_debug_class_statement_location_uses_source_line_not_ast_repr():
    session = make_debug_session(
        "Class Machine {\n" "  init() {\n" "    print 1;\n" "  }\n" "}\n"
    )

    outputs = session.format_current_location()

    assert outputs == ["[DEBUG] 1번째 줄에서 정지 -> Class Machine {"]
    assert "ClassStmt" not in outputs[0]
    assert "FunctionStmt" not in outputs[0]
