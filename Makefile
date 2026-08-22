SHELL := /bin/bash

all: install run

install:
	pip install -r requirements.txt

run:
	python main.py

build:
	python -m build

clean:
	rm -rf __pycache__ .mypy_cache
	rm -rf src/__pycache__ src/.mypy_cache

lint:
	flake8 src/simulation.py src/logic.py src/data.py main.py src/parser.py
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 src/simulation.py src/logic.py src/data.py main.py src/parser.py
	mypy . --strict

.PHONY: install run debug clean lint lint-strict
