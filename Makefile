SHELL := bash
PATH := ./venv/bin:${PATH}
PYTHON=python3.7


all: test

venv:
		$(PYTHON) -m venv --prompt stpmex venv
		source venv/bin/activate
		pip install --quiet --upgrade pip

clean:
		find . -name '__pycache__' -exec rm -r "{}" +
		find . -name '*.pyc' -delete
		find . -name '*~' -delete

install-dev:
		pip install -q -e .[dev]

test: lint
		python setup.py test

lint:
		pycodestyle stpmex/ test_stpmex.py setup.py

release: clean
		python setup.py sdist bdist_wheel
		twine upload dist/* --verbose

.PHONY: all clean install-dev test lint
