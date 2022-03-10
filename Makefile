all: install
	pip install wheel
	python setup.py sdist bdist_wheel

install:
	pip install -e .

format:
	autopep8 -r . -i
	black . -l 79
