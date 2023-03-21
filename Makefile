all: install
	pip install wheel
	python setup.py sdist bdist_wheel

install:
	pip install -e .

format:
	black . -l 79
