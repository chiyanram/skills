.PHONY: check lint test help

PYTHON ?= python3

check: lint test ## run everything CI runs

lint: ## skill frontmatter, one version, links, size budgets, packaging, README index, skill routers, plugin validate
	$(PYTHON) scripts/check_skills.py .
	$(PYTHON) scripts/check_versions.py .
	$(PYTHON) scripts/check_links.py .
	$(PYTHON) scripts/check_sizes.py .
	$(PYTHON) scripts/check_plugin.py .
	$(PYTHON) scripts/check_index.py .
	$(PYTHON) scripts/check_routers.py .
	claude plugin validate --strict .
	claude plugin validate --strict --profile directory plugins/rulebook

test: ## each check against its planted fixtures, and each review/ builder
	$(PYTHON) -m unittest discover --start-directory tests --top-level-directory .

help: ## list the targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-6s %s\n", $$1, $$2}'
