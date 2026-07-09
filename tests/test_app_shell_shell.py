from app.shell.file_mode import FileMode
from app.shell.runner import CodeFabRunner
from app.shell.shell import PromptShell


def make_shell():
    return PromptShell()


def test_run_line_executes_code_with_assembler():
    shell = make_shell()

    outputs = shell.run_line("print 37;")

    assert outputs == ["37"]


def test_run_line_heart_operator_computes_name_compatibility():
    shell = make_shell()

    outputs = shell.run_line('var a = "김철수" ♡ "박이안"; print a;')

    assert outputs == ["75"]


def test_run_line_strips_input():
    shell = make_shell()

    outputs = shell.run_line("  print 37;  ")

    assert outputs == ["37"]


def test_run_line_saves_history():
    shell = make_shell()

    shell.run_line("print 37;")
    shell.run_line("print 38;")

    assert shell.history == ["print 37;", "print 38;"]


def test_ctrlc_recommends_most_frequent_exact_command():
    shell = make_shell()

    shell.run_line("print 36;")
    shell.run_line("print 36;")
    shell.run_line("print 35;")

    outputs = shell.run_line("ctrlc")

    assert outputs == [
        "Ctrl+C 추천 명령어: print 36;",
        "ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.",
    ]


def test_ctrlc_recommends_recent_command_when_frequency_is_same():
    shell = make_shell()

    shell.run_line("print 36;")
    shell.run_line("print 35;")

    outputs = shell.run_line("ctrlc")

    assert outputs == [
        "Ctrl+C 추천 명령어: print 35;",
        "ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.",
    ]


def test_ctrlv_runs_recommended_command():
    shell = make_shell()

    shell.run_line("print 36;")
    shell.run_line("print 36;")
    shell.run_line("print 35;")

    shell.run_line("ctrlc")
    outputs = shell.run_line("ctrlv")

    assert outputs == ["36"]


def test_ctrlv_without_recommendation_returns_message():
    shell = make_shell()

    outputs = shell.run_line("ctrlv")

    assert outputs == ["먼저 ctrlc 로 추천 명령어를 생성해주세요."]


def test_ctrlc_without_history_returns_message():
    shell = make_shell()

    outputs = shell.run_line("ctrlc")

    assert outputs == ["추천할 명령어가 없습니다."]


def test_exit_stops_shell():
    shell = make_shell()

    outputs = shell.run_line("exit")

    assert outputs == ["Bye!"]
    assert shell.is_running is False


def test_quit_stops_shell():
    shell = make_shell()

    outputs = shell.run_line("quit")

    assert outputs == ["Bye!"]
    assert shell.is_running is False


def test_empty_input_returns_empty_output():
    shell = make_shell()

    outputs = shell.run_line("")

    assert outputs == []


def test_shell_commands_are_not_saved_to_history():
    shell = make_shell()

    shell.run_line("print 36;")
    shell.run_line("ctrlc")
    shell.run_line("ctrlv")
    shell.run_line("exit")

    assert shell.history == ["print 36;"]


def test_history_size_keeps_recent_inputs_only():
    shell = PromptShell(history_size=3)

    shell.run_line("print 1;")
    shell.run_line("print 2;")
    shell.run_line("print 3;")
    shell.run_line("print 4;")

    assert shell.history == ["print 2;", "print 3;", "print 4;"]


def test_ctrlc_recommends_with_limited_history():
    shell = PromptShell(history_size=3)

    shell.run_line("print 1;")
    shell.run_line("print 2;")
    shell.run_line("print 2;")
    shell.run_line("print 3;")

    outputs = shell.run_line("ctrlc")

    assert shell.history == ["print 2;", "print 2;", "print 3;"]
    assert outputs == [
        "Ctrl+C 추천 명령어: print 2;",
        "ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.",
    ]


def test_file_mode_executes_source_file(tmp_path):
    source_file = tmp_path / "sample.txt"
    source_file.write_text("print 1 + 2;", encoding="utf-8")

    outputs = FileMode().run_file(str(source_file))

    assert outputs == ["3"]


def test_file_mode_returns_error_when_file_not_found(tmp_path):
    missing_file = tmp_path / "missing.txt"

    outputs = FileMode().run_file(str(missing_file))

    assert outputs == [f"Error: file not found: {missing_file}"]


def test_runner_returns_outputs_before_runtime_error(mocker):
    runner = CodeFabRunner()
    runner.executor.outputs.append("before")

    mocker.patch.object(runner.tokenizer, "tokenize", return_value=[])
    mocker.patch("app.shell.runner.Assembler").return_value.parse.return_value = []
    mocker.patch.object(runner.checker, "check", return_value=[])
    mocker.patch.object(
        runner.executor,
        "execute",
        side_effect=Exception("runtime error"),
    )

    outputs = runner.run_code("invalid code")

    assert outputs == ["Error: runtime error"]


def test_file_mode_stops_immediately_when_runtime_error_occurs(tmp_path):
    source_file = tmp_path / "sample.txt"
    source_file.write_text(
        "print 1;\n" "print 10 / 0;\n" "print 3;\n",
        encoding="utf-8",
    )

    outputs = FileMode().run_file(str(source_file))

    assert outputs == [
        "1",
        "Error at line 2: Division by zero.",
    ]


def test_file_mode_prints_runtime_error_with_line_number(tmp_path):
    source_file = tmp_path / "sample.txt"
    source_file.write_text(
        "print 1;\n" "print 10 / 0;\n" "print 3;\n",
        encoding="utf-8",
    )

    outputs = FileMode().run_file(str(source_file))

    assert outputs == [
        "1",
        "Error at line 2: Division by zero.",
    ]


def test_file_mode_stops_immediately_after_runtime_error(tmp_path):
    source_file = tmp_path / "sample.txt"
    source_file.write_text(
        "print 1;\n" "print 10 / 0;\n" "print 999;\n",
        encoding="utf-8",
    )

    outputs = FileMode().run_file(str(source_file))

    assert "999" not in outputs
    assert outputs == [
        "1",
        "Error at line 2: Division by zero.",
    ]
