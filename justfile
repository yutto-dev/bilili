run:
  python3 -m bilili

test:
  python3 -m pytest -m '(api or e2e) and not ci_only'
  just clean

release:
  python3 setup.py upload
  just clean-builds

install:
  python3 setup.py build
  python3 setup.py install
  just clean-builds

upgrade-pip:
  python3 -m pip install --upgrade --pre bilili

clean:
  find . -name "*- bilibili" -print0 | xargs -0 rm -rf
  rm -rf tmp/
  rm -rf .pytest_cache/

clean-builds:
  rm -rf build/
  rm -rf dist/
  rm -rf bilili.egg-info/

docs:
  cd docs/ && yarn dev
