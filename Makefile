.PHONY: check lint test index size help

PYTHON ?= python3

check: lint test ## run everything CI runs

lint: ## skill frontmatter, one version, links, size budgets, packaging, router index, skill routers, provenance, ledger, routing, process files, toolbox, settings keys, plugin validate
	$(PYTHON) scripts/check_skills.py .
	$(PYTHON) scripts/check_versions.py .
	$(PYTHON) scripts/check_links.py .
	$(PYTHON) scripts/check_sizes.py .
	$(PYTHON) scripts/check_plugin.py .
	$(PYTHON) scripts/check_index.py .
	$(PYTHON) scripts/check_routers.py .
	$(PYTHON) scripts/check_provenance.py .
	$(PYTHON) scripts/check_ledger.py .
	$(PYTHON) scripts/check_routing.py .
	$(PYTHON) scripts/check_process.py .
	$(PYTHON) scripts/check_toolbox.py .
	$(PYTHON) scripts/check_settings_keys.py .
	claude plugin validate --strict .
	for plugin in plugins/*/; do claude plugin validate --strict --profile directory $$plugin || exit 1; done

test: ## each check against its planted fixtures, the index builder and the release config
	$(PYTHON) -m unittest discover --start-directory tests --top-level-directory .

index: ## rebuild each skill router's reference table from its references
	$(PYTHON) scripts/build_index.py .

size: ## changed lines and files against PD9
	$(PYTHON) scripts/branch_size.py origin/main

help: ## list the targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-6s %s\n", $$1, $$2}'
