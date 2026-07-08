# Use the project venv directly so targets work without activation.
VENV := .venv/bin

.PHONY: install lint test

install:
	pip install -r requirements-dev.txt

# Run formatters and linter (same trio as the README's PR checklist).
# black and isort rewrite files in place; ruff --fix auto-fixes what it can
# and reports anything that still needs a manual change.
lint:
	$(VENV)/black .
	$(VENV)/isort .
	$(VENV)/ruff check --fix .

test:
	PYTHONPATH=. $(VENV)/pytest -q
