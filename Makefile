SHELL := /bin/bash

all: run

install:
	pip install -r requirements.txt

run:
	python main.py map.txt

debug:
	python -m pdb main.py

clean:
	rm -rf __pycache__ .mypy_cache
	rm -rf src/__pycache__ src/.mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run debug clean lint lint-strict
