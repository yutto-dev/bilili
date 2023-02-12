set positional-arguments

PYTHON := ".venv/bin/python"

create-venv:
  python3 -m venv .venv

install-deps:
  {{PYTHON}} -m pip install --upgrade pip
  {{PYTHON}} -m pip install -r requirements.txt
  {{PYTHON}} -m pip install -r requirements-dev.txt

run *ARGS:
  {{PYTHON}} -m bilili {{ARGS}}

test:
  {{PYTHON}} -m pytest -m '(api or e2e) and not ci_only'
  just clean

publish:
  {{PYTHON}} setup.py upload
  just clean-builds

install:
  {{PYTHON}} setup.py build
  {{PYTHON}} setup.py install
  just clean-builds

clean:
  find . -name "*- bilibili" -print0 | xargs -0 rm -rf
  rm -rf tmp/
  rm -rf .pytest_cache/

clean-builds:
  rm -rf build/
  rm -rf dist/
  rm -rf bilili.egg-info/

docs:
  cd docs/ && pnpm dev

fmt:
  {{PYTHON}} -m black . --line-length=120
  {{PYTHON}} -m isort . --profile=black --line-length=120

ci-api-test:
  {{PYTHON}} -m pytest -m "api and not ci_skip"
  just clean

ci-e2e-test:
  {{PYTHON}} -m pytest -m "e2e and not ci_skip"
  just clean
