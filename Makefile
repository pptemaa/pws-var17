.PHONY: run test lint

run:
	python3 src/repl.py

test:
	python3 -m pytest tests/ -v

lint:
	python3 -m flake8 src/ tests/ --max-line-length=80
