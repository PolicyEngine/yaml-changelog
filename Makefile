all: install
	pip install wheel build
	python -m build

install:
	pip install -e .

format:
	black . -l 79

changelog:
	python .github/bump_version.py
	towncrier build --yes --version $$(python -c "import re; print(re.search(r'version = \"(.+?)\"', open('pyproject.toml').read()).group(1))")
