from shell import PromptShell

def make_shell():
    return PromptShell()


def test_run_line_executes_code_with_assembler():
    shell = make_shell()

    outputs = shell.run_line("print 37;")

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