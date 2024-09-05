set positional-arguments

VERSION := `uv run python -c "import sys; from bilili.__version__ import VERSION as bilili_version; sys.stdout.write(bilili_version)"`

install:
  uv sync

clean-venv:
  rm -rf .venv

run *ARGS:
  uv run bilili {{ARGS}}

test:
  uv run pytest -m '(api or e2e) and not ci_only'
  just clean

build:
  uv build

release:
  @echo 'Tagging {{VERSION}}...'
  git tag {{VERSION}}
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

ci-install:
  just install

ci-api-test:
  uv run pytest -m "api and not ci_skip" --reruns 3 --reruns-delay 1
  just clean

ci-e2e-test:
  uv run pytest -m "e2e and not ci_skip"
  just clean
