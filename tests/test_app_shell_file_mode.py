from app.shell.file_mode import FileMode


def test_file_mode_resolves_import_relative_to_source_file(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    main_file = project_dir / "main.cfab"
    sum_file = project_dir / "sum.txt"

    main_file.write_text(
        'import "sum.txt" alias sum;\n' "print sum.answer;\n",
        encoding="utf-8",
    )

    sum_file.write_text(
        "var answer = 42;\n",
        encoding="utf-8",
    )

    other_dir = tmp_path / "other"
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)

    outputs = FileMode().run_file(str(main_file))

    assert outputs == ["42"]
