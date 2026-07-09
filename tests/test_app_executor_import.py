import pytest

from app.assembler.assembler import Assembler
from app.assembler.tokenizer import Tokenizer
from app.exceptions import CodeFabRuntimeError
from app.executor.executor import Executor


def write(tmp_path, name, content):
    (tmp_path / name).write_text(content, encoding="utf-8")


def run(tmp_path, source):
    tokens = Tokenizer().tokenize(source)
    statements = Assembler(tokens).parse()

    executor = Executor(import_base_dir=str(tmp_path))
    executor.execute(statements)
    return executor


def test_import_alias_call_and_print_result(tmp_path):
    write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")

    executor = run(
        tmp_path,
        'import "sum.txt" alias sum;\n'
        "var result = sum.add(1, 2);\n"
        "print result;\n",
    )

    assert executor.outputs == ["3"]


def test_import_exposes_var_declaration(tmp_path):
    write(tmp_path, "constants.txt", "var pi = 3.14;")

    executor = run(
        tmp_path,
        'import "constants.txt" alias constants;\n' "print constants.pi;\n",
    )

    assert executor.outputs == ["3.14"]


def test_import_exposes_class_declaration(tmp_path):
    write(
        tmp_path,
        "shapes.txt",
        "Class Point {\n"
        "  init(x) { This.x = x; }\n"
        "}\n",
    )

    executor = run(
        tmp_path,
        'import "shapes.txt" alias shapes;\n'
        "var p = shapes.Point(5);\n"
        "print p.x;\n",
    )

    assert executor.outputs == ["5"]


def test_import_missing_file_raises(tmp_path):
    with pytest.raises(CodeFabRuntimeError):
        run(tmp_path, 'import "missing.txt" alias missing;\n')


def test_circular_import_raises(tmp_path):
    write(tmp_path, "a.txt", 'import "b.txt" alias b;')
    write(tmp_path, "b.txt", 'import "a.txt" alias a;')

    with pytest.raises(CodeFabRuntimeError):
        run(tmp_path, 'import "a.txt" alias a;\n')
