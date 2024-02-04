TEST = python -m pytest 
TEST_ARGS = -s --verbose --color=yes
CHECK_TYPE = mypy --strict --allow-untyped-decorators --ignore-missing-imports
CHECK_STYLE = flake8
FIX_STYLE = autopep8 --in-place --recursive --aggressive --aggressive

.PHONY: all
all: check-style check-type run-test

.PHONY: check-type
check-type:
	$(CHECK_TYPE) kattis_cli

.PHONY: check-style
check-style:
	$(CHECK_STYLE) kattis_cli

# discover and run all tests
.PHONY: run-test
run-test:
	$(TEST) $(TEST_ARGS) tests

.PHONY: fix-style
fix-style:
	$(FIX_STYLE) kattis_cli
	$(FIX_STYLE) tests

.PHONY: clean
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .hypothesis
	rm -rf .coverage
	
