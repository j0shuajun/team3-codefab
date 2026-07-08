# Use the project venv's Python directly so targets work without activation.
# venv layout differs by OS: POSIX uses bin/, Windows uses Scripts/.
ifeq ($(OS),Windows_NT)
    PYTHON := .venv/Scripts/python.exe
else
    PYTHON := .venv/bin/python
endif

.PHONY: install lint test

install:
	pip install -r requirements-dev.txt

# Run formatters and linter (same trio as the README's PR checklist).
# black and isort rewrite files in place; ruff --fix auto-fixes what it can
# and reports anything that still needs a manual change.
lint:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	$(PYTHON) -m ruff check --fix .

# pytest resolves package imports via pyproject.toml's [tool.pytest.ini_options]
# pythonpath setting, so no PYTHONPATH env var (shell-syntax dependent) is needed.
test:
	$(PYTHON) -m pytest -q
