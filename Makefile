.PHONY: test lint run-api example

test:
	pytest

lint:
	ruff check src tests examples

run-api:
	uvicorn piis.api.main:app --reload

example:
	python examples/basic_pipeline.py
