# notebooklm-py — run with uv (https://docs.astral.sh/uv/)
# Usage: make install-dev  then  make test | make check | etc.

.PHONY: help venv install install-browser install-dev test test-cov test-e2e format lint typecheck check clean

# Default: show targets
help:
	@echo "notebooklm-py (uv)"
	@echo ""
	@echo "Setup (run once):"
	@echo "  make venv          Create .venv"
	@echo "  make install       Install package (editable, no extras)"
	@echo "  make install-browser  Install with [browser] + playwright chromium"
	@echo "  make install-dev    Install with [all] (browser + dev deps) + playwright"
	@echo ""
	@echo "Tests:"
	@echo "  make test          Run pytest (excludes e2e)"
	@echo "  make test-cov      Run pytest with coverage"
	@echo "  make test-e2e      Run e2e tests (requires auth)"
	@echo ""
	@echo "Code quality (pre-commit):"
	@echo "  make format        ruff format src/ tests/"
	@echo "  make lint          ruff check src/ tests/"
	@echo "  make typecheck     mypy src/notebooklm --ignore-missing-imports"
	@echo "  make check         format + lint + typecheck + test"
	@echo ""
	@echo "Other:"
	@echo "  make clean         Remove .venv and cache dirs"

# Create venv (optional; uv run will create if missing)
venv:
	uv venv .venv
	@echo "Activate with: source .venv/bin/activate"

# Install editable, no extras
install: venv
	uv pip install -e .

# Install with browser support (for login)
install-browser: venv
	uv pip install -e ".[browser]"
	uv run playwright install chromium

# Install with all extras (dev + browser)
install-dev: venv
	uv pip install -e ".[all]"
	uv run playwright install chromium

test:
	uv run pytest

test-cov:
	uv run pytest --cov

test-e2e:
	uv run pytest tests/e2e -m e2e

format:
	uv run ruff format src/ tests/

lint:
	uv run ruff check src/ tests/

typecheck:
	uv run mypy src/notebooklm --ignore-missing-imports

check: format lint typecheck test
	@echo "All checks passed."

clean:
	rm -rf .venv
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
