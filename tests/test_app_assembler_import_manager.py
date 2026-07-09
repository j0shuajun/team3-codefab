import os

import pytest

from app.assembler.import_manager import ImportManager
from app.exceptions import CodeFabRuntimeError


def write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


class TestResolvePath:
    def test_relative_path_resolves_against_base_dir(self, tmp_path):
        manager = ImportManager(base_dir=str(tmp_path))

        resolved = manager.resolve_path("sum.txt")

        assert resolved == os.path.abspath(os.path.join(str(tmp_path), "sum.txt"))

    def test_relative_path_resolves_against_explicit_base_dir(self, tmp_path):
        manager = ImportManager(base_dir="/somewhere/else")

        resolved = manager.resolve_path("sum.txt", base_dir=str(tmp_path))

        assert resolved == os.path.abspath(os.path.join(str(tmp_path), "sum.txt"))

    def test_absolute_path_ignores_base_dir(self, tmp_path):
        manager = ImportManager(base_dir="/somewhere/else")
        absolute = write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")

        resolved = manager.resolve_path(absolute)

        assert resolved == os.path.abspath(absolute)


class TestRead:
    def test_read_returns_file_contents(self, tmp_path):
        write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")
        manager = ImportManager(base_dir=str(tmp_path))

        assert manager.read("sum.txt") == "Func add(a, b) { return a + b; }"

    def test_read_missing_file_raises(self, tmp_path):
        manager = ImportManager(base_dir=str(tmp_path))

        with pytest.raises(CodeFabRuntimeError):
            manager.read("missing.txt")

    def test_read_caches_content_after_first_read(self, tmp_path):
        path = write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")
        manager = ImportManager(base_dir=str(tmp_path))

        first = manager.read("sum.txt")
        os.remove(path)

        assert manager.read("sum.txt") == first


class TestLoad:
    def test_load_returns_parsed_statements(self, tmp_path):
        from app.assembler.statement import FunctionStmt

        write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")
        manager = ImportManager(base_dir=str(tmp_path))

        statements = manager.load("sum.txt")

        assert len(statements) == 1
        assert isinstance(statements[0], FunctionStmt)
        assert statements[0].name.origin == "add"

    def test_load_missing_file_raises(self, tmp_path):
        manager = ImportManager(base_dir=str(tmp_path))

        with pytest.raises(CodeFabRuntimeError):
            manager.load("missing.txt")


class TestImporting:
    def test_importing_yields_resolved_path(self, tmp_path):
        write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")
        manager = ImportManager(base_dir=str(tmp_path))

        with manager.importing("sum.txt") as resolved:
            assert resolved == os.path.abspath(os.path.join(str(tmp_path), "sum.txt"))

    def test_importing_releases_stack_after_exit(self, tmp_path):
        write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")
        manager = ImportManager(base_dir=str(tmp_path))

        with manager.importing("sum.txt"):
            pass

        with manager.importing("sum.txt"):
            pass

    def test_importing_same_file_while_already_importing_raises(self, tmp_path):
        write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")
        manager = ImportManager(base_dir=str(tmp_path))

        with manager.importing("sum.txt"):
            with pytest.raises(CodeFabRuntimeError):
                with manager.importing("sum.txt"):
                    pass

    def test_transitive_circular_import_raises(self, tmp_path):
        write(tmp_path, "a.txt", 'import "b.txt" alias b;')
        write(tmp_path, "b.txt", 'import "a.txt" alias a;')
        manager = ImportManager(base_dir=str(tmp_path))

        with manager.importing("a.txt"):
            with manager.importing("b.txt"):
                with pytest.raises(CodeFabRuntimeError):
                    with manager.importing("a.txt"):
                        pass

    def test_stack_is_released_after_exception_inside_block(self, tmp_path):
        write(tmp_path, "sum.txt", "Func add(a, b) { return a + b; }")
        manager = ImportManager(base_dir=str(tmp_path))

        with pytest.raises(ValueError):
            with manager.importing("sum.txt"):
                raise ValueError("boom")

        with manager.importing("sum.txt"):
            pass

    def test_nested_import_resolves_relative_to_importing_file(self, tmp_path):
        nested_dir = tmp_path / "lib"
        nested_dir.mkdir()
        write(tmp_path, "a.txt", 'import "lib/b.txt" alias b;')
        write(nested_dir, "b.txt", "Func helper() { return 1; }")
        manager = ImportManager(base_dir=str(tmp_path))

        with manager.importing("a.txt") as a_resolved:
            with manager.importing(
                "b.txt", base_dir=os.path.dirname(a_resolved) + "/lib"
            ) as b_resolved:
                assert manager.read(b_resolved) == "Func helper() { return 1; }"
