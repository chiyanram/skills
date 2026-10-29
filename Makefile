.PHONY: lint test

PYTHON ?= python3

lint:
	$(PYTHON) scripts/check_skills.py .
	$(PYTHON) scripts/check_versions.py .
	$(PYTHON) scripts/check_links.py .
	$(PYTHON) scripts/check_sizes.py .
	$(PYTHON) scripts/check_plugin.py .
	claude plugin validate --strict .
	claude plugin validate --strict --profile directory plugins/rulebook

test:
	$(PYTHON) -m unittest discover --start-directory tests --top-level-directory .
