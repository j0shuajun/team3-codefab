from app.assembler.assembler import Assembler
from app.shell.debug_mode import DebugMode, DebugSession
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


def test_debug_current_location_uses_source_line_not_ast_repr():
    session = make_debug_session("var a = 3;\n" "var b = a + 1;\n")

    outputs = session.format_current_location()

    assert outputs == ["[DEBUG] 1번째 줄에서 정지 -> var a = 3;"]
    assert "VarStmt" not in outputs[0]


def test_debug_step_prints_next_location_with_source_line():
    session = make_debug_session("var a = 3;\n" "var b = a + 1;\n")

    outputs = session.process_command("step")

    assert outputs == ["[DEBUG] 2번째 줄에서 정지 -> var b = a + 1;"]


def test_debug_break_command_uses_pdf_style_message():
    session = make_debug_session("var a = 3;\n" "print a;\n")

    outputs = session.process_command("break 2")

    assert outputs == ["[DEBUG] 2번째 줄에 breakpoint 설정"]


def test_debug_continue_stops_at_breakpoint_with_source_line():
    session = make_debug_session("var a = 3;\n" "var b = a + 1;\n" "print b;\n")

    session.process_command("break 3")
    outputs = session.process_command("continue")

    assert outputs == ["[DEBUG] 3번째 줄에서 정지 (breakpoint) -> print b;"]


def test_debug_remove_breakpoint_uses_pdf_style_message():
    session = make_debug_session("var a = 3;\n" "print a;\n")

    session.process_command("break 2")
    outputs = session.process_command("remove 2")

    assert outputs == ["[DEBUG] 2번째 줄 breakpoint 해제"]


def test_debug_breakpoints_prints_registered_breakpoints():
    session = make_debug_session("var a = 3;\n" "var b = 4;\n" "print a + b;\n")

    session.process_command("break 2")
    session.process_command("break 3")

    outputs = session.process_command("breakpoints")

    assert outputs == ["[DEBUG] breakpoint 목록: 2, 3"]


def test_debug_watch_command_uses_watch_prefix():
    session = make_debug_session("var a = 3;\n" "print a;\n")

    outputs = session.process_command("watch a")

    assert outputs == ["[WATCH] 'a' 감시 등록"]


def test_debug_step_prints_watches_after_location():
    session = make_debug_session("var a = 3;\n" "var b = a + 1;\n")

    session.process_command("watch a")
    outputs = session.process_command("step")

    assert outputs == [
        "[DEBUG] 2번째 줄에서 정지 -> var b = a + 1;",
        "[WATCH] a = 3",
    ]


def test_debug_unwatch_command_uses_watch_prefix():
    session = make_debug_session("var a = 3;\n" "print a;\n")

    session.process_command("watch a")
    outputs = session.process_command("unwatch a")

    assert outputs == ["[WATCH] 'a' 감시 해제"]


def test_debug_watches_prints_current_watch_values():
    session = make_debug_session("var a = 3;\n" "var b = a + 1;\n")

    session.process_command("watch a")
    session.process_command("step")

    outputs = session.process_command("watches")

    assert outputs == ["[WATCH] a = 3"]


def test_debug_watches_prints_undefined_for_missing_variable():
    session = make_debug_session("var a = 3;\n" "print a;\n")

    session.process_command("watch missing")

    outputs = session.process_command("watches")

    assert outputs == ["[WATCH] missing = <undefined>"]


def test_debug_inspect_prints_current_scope_readably():
    session = make_debug_session("var a = 3;\n" "var b = a + 1;\n")

    session.process_command("step")

    outputs = session.process_command("inspect")

    assert outputs[0] == "[DEBUG] 현재 scope 변수"
    assert "- a = 3" in outputs


def test_debug_next_does_not_enter_block_and_prints_next_location():
    session = make_debug_session("{\n" "  print 1;\n" "}\n" "print 2;\n")

    outputs = session.process_command("next")

    assert outputs == [
        "1",
        "[DEBUG] 4번째 줄에서 정지 -> print 2;",
    ]


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


def test_debug_run_session_prints_source_loading_and_initial_location(
    monkeypatch,
    capsys,
):
    session = make_debug_session("var a = 3;\n" "print a;\n")

    debug_mode = DebugMode()
    monkeypatch.setattr("builtins.input", lambda prompt: "exit")

    debug_mode.run_session(session, file_path="sample.cf")

    captured = capsys.readouterr().out

    assert "[DEBUG] 소스코드 로딩: sample.cf" in captured
    assert "[DEBUG] 1번째 줄에서 정지 -> var a = 3;" in captured
    assert "VarStmt" not in captured
