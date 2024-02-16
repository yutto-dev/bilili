set positional-arguments

create-venv:
  uv venv

clean-venv:
  rm -rf .venv

install:
  uv pip install -e ".[dev]"

run *ARGS:
  python -m bilili {{ARGS}}

test:
  python -m pytest -m '(api or e2e) and not ci_only'
  just clean

build:
  python -m build

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
  python -m ruff check .

fmt:
  python -m ruff format .

ci-api-test:
  python -m pytest -m "api and not ci_skip" --reruns 3 --reruns-delay 1
  just clean

ci-e2e-test:
  python -m pytest -m "e2e and not ci_skip"
  just clean
