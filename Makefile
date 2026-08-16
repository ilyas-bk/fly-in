SHELL := /bin/bash

install:
	pip install -r requirements.txt
	pip install flake8 mypy

run:
	. .venv/bin/activate && python simulation.py

build:
	python -m build

clean:
	rm -rf __pycache__ .mypy_cache
	rm -rf src/__pycache__ src/.mypy_cache

lint:
	. .venv/bin/activate && flake8 simulation.py logic.py data.py main.py parser.py

lint-strict:
	flake8
	mypy . --strict

.PHONY: install run debug clean lint lint-strict
