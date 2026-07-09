from assembler.assembler import Assembler
from shell.debug_mode import DebugSession
from shell.shell import CodeFabRunner


def make_debug_session(source):
    runner = CodeFabRunner()
    tokens = runner.tokenizer.tokenize(source)
    statements = Assembler(tokens).parse()
    return DebugSession(runner, statements)


def test_debug_step_executes_current_statement():
    session = make_debug_session("var a = 10;\n" "print a;\n")

    assert session.process_command("step") == []
    assert session.process_command("step") == ["10"]


def test_debug_watch_prints_variable_after_step():
    session = make_debug_session("var a = 10;\n" "a = a + 5;\n")

    assert session.process_command("watch a") == ["Watch added: a"]
    assert session.process_command("step") == ["a = 10"]
    assert session.process_command("step") == ["a = 15"]


def test_debug_watches_prints_current_watch_values():
    session = make_debug_session("var a = 10;\n")

    session.process_command("watch a")
    session.process_command("step")

    assert session.process_command("watches") == ["a = 10"]


def test_debug_inspect_prints_current_scope_values():
    session = make_debug_session("var a = 10;\n")

    session.process_command("step")

    outputs = session.process_command("inspect")

    assert "a = 10" in outputs


def test_debug_breakpoint_stops_before_line():
    session = make_debug_session("var a = 10;\n" "print a;\n" "print 20;\n")

    assert session.process_command("break 2") == ["Breakpoint added at line 2."]

    outputs = session.process_command("continue")

    assert outputs == ["Stopped at breakpoint line 2."]


def test_debug_remove_breakpoint():
    session = make_debug_session("var a = 10;\n" "print a;\n")

    session.process_command("break 2")
    assert session.process_command("remove 2") == ["Breakpoint removed at line 2."]
    assert session.process_command("breakpoints") == ["No breakpoints."]


def test_debug_continue_runs_until_breakpoint():
    session = make_debug_session("var a = 10;\n" "a = a + 5;\n" "print a;\n")

    session.process_command("break 3")

    assert session.process_command("continue") == ["Stopped at breakpoint line 3."]
    assert session.process_command("step") == ["15"]


def test_debug_step_reports_if_condition_error_line():
    session = make_debug_session("if (10 / 0) {\n" "  print 1;\n" "}\n" "print 2;\n")

    outputs = session.process_command("step")

    assert outputs == ["Error at line 1: Division by zero."]

def test_debug_continue_stops_at_breakpoint_inside_for_loop():
    session = make_debug_session(
        """
var total = 0;
for (var i = 0; i < 3; i = i + 1) {
  total = total + i;
  print total;
}
print "done";
"""
    )

    session.process_command("break 4")
    outputs = session.process_command("continue")

    assert outputs == ["Stopped at breakpoint line 4."]
