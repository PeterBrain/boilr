PYTHON = python3

.PHONY: install install_dev test run clean

install:
	# @$(PYTHON) -m pip install -e .
	@$(PYTHON) -m pip install -r requirements.txt

install_dev:
	# @$(PYTHON) -m pip install -e ".[dev]"
	@$(PYTHON) -m pip install -r requirements_dev.txt

test:
	@$(PYTHON) -m pytest -v --cov=boilr

run:
	@$(PYTHON) -m boilr run

clean:
	@rm -rf dist build *.egg-info
	@find . -name "__pycache__" -exec rm -rf {} +
