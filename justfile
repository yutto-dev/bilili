set positional-arguments

VERSION := `grep -oE '\d+\.\d+\.\d+(.+[^"])?' src/bilili/__version__.py`
PYTHON := ".venv/bin/python"

create-venv:
  python3 -m venv .venv

install:
  {{PYTHON}} -m pip install -e ".[dev]"

run *ARGS:
  {{PYTHON}} -m bilili {{ARGS}}

test:
  {{PYTHON}} -m pytest -m '(api or e2e) and not ci_only'
  just clean

build:
  {{PYTHON}} -m build

release:
  git tag v{{VERSION}}
  git push --tags

clean:
  find . -name "*- bilibili" -print0 | xargs -0 rm -rf
  rm -rf tmp/
  rm -rf .pytest_cache/

clean-builds:
  rm -rf build/
  rm -rf dist/
  rm -rf *.egg-info/

docs:
  cd docs/ && pnpm dev

lint:
  {{PYTHON}} -m ruff .

fmt:
  {{PYTHON}} -m black .
  {{PYTHON}} -m isort .

ci-api-test:
  {{PYTHON}} -m pytest -m "api and not ci_skip" --reruns 3 --reruns-delay 1
  just clean

ci-e2e-test:
  {{PYTHON}} -m pytest -m "e2e and not ci_skip"
  just clean
