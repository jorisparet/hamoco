PROJECT = hamoco

.PHONY: test coverage

test:
	python -m unittest discover -s tests

coverage:
	coverage run --source hamoco -m unittest discover -s tests
	coverage report -m
