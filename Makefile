TEST = python -m pytest 
TEST_ARGS = --verbose --color=yes
TYPE_CHECK = mypy --strict --allow-untyped-decorators --ignore-missing-imports
STYLE_CHECK = flake8
STYLE_FIX = autopep8 --in-place --recursive --aggressive --aggressive

.PHONY: all
all: check-style check-type run-test clean

.PHONY: check-type
type-check:
	$(TYPE_CHECK) .

.PHONY: check-style
check-style:
	$(STYLE_CHECK) .

# discover and run all tests
.PHONY: run-test
run-test:
	$(TEST) $(TEST_ARGS) tests

.PHONY: clean
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .hypothesis
	rm -rf .coverage
	rm -rf kattis_cli/__pycache__
	
.PHONY: fix-style
fix-style:
	$(STYLE_FIX) .
