.PHONY: ci
ci:
	uv sync
	uv pip install -e .
	uv run ruff format .
	uv run ruff check .
	uv run mypy src/
	uv run pytest

.PHONY: clean
clean:
	uv pip uninstall super-lean-management-engine
	rm -rf .pytest_cache __pycache__ src/dual_board_kanban/__pycache__ tests/__pycache__ .coverage htmlcov build dist *.egg-info src/super_lean_management_engine.egg-info
