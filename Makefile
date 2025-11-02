# Makefile for Recator

.PHONY: help clean build test venv install-dev publish-test publish

# Bump part for versioning on publish: patch (default), minor, or major
PART ?= patch

# Python interpreter used to create venv (override: make PY=python3.11 venv)
PY ?= python3

help:
	@echo "Targets:"
	@echo "  make venv           - create local venv in venv (PY=$(PY))"
	@echo "  make install-dev    - install package in editable mode with dev deps"
	@echo "  make build          - build sdist and wheel"
	@echo "  make test           - run pytest"
	@echo "  make publish-test   - upload to TestPyPI (auto-bump: $(PART))"
	@echo "  make publish        - upload to PyPI (auto-bump: $(PART))"
	@echo "Variables: PART=patch|minor|major (default: patch)"
	@echo "           PY=python3.11 (override python used for venv)"
	@echo "  make clean          - remove build artifacts"

venv:
	$(PY) -m venv venv
	. venv/bin/activate; python -m ensurepip --upgrade || true
	. venv/bin/activate; python -m pip install -U pip

install-dev:
	. venv/bin/activate; pip install -e ".[dev]"

build:
	. venv/bin/activate; python -m pip install build
	. venv/bin/activate; python -m build

test:
	. venv/bin/activate; pytest -q

publish-test:
	chmod +x scripts/publish.sh
	. venv/bin/activate; ./scripts/publish.sh test $(PART)

publish:
	chmod +x scripts/publish.sh
	. venv/bin/activate; ./scripts/publish.sh pypi $(PART)

clean:
	rm -rf build/ dist/ *.egg-info **/*.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
