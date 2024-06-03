set positional-arguments

PYTHON := ".venv/bin/python"

create-venv:
  uv venv

clean-venv:
  rm -rf .venv

install:
  uv pip install -e ".[dev]"

run *ARGS:
  uv run bilili -- {{ARGS}}

test:
  uv run pytest -m '(api or e2e) and not ci_only'
  just clean

build:
  uv tool run --from build python -m build --installer uv .

release version:
  @echo 'Tagging {{version}}...'
  git tag {{version}}
  @echo 'Push to GitHub to trigger publish process...'
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
  uv run ruff check .

fmt:
  uv run ruff format .

ci-api-test:
  uv run pytest -m "api and not ci_skip" --reruns 3 --reruns-delay 1
  just clean

ci-e2e-test:
  uv run pytest -m "e2e and not ci_skip"
  just clean
