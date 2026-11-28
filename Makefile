.PHONY: check lint test index size help

PYTHON ?= python3

check: lint test ## run everything CI runs

lint: ## skill frontmatter, one version, links, size budgets, packaging, skill list and AGENTS.md block, provenance, glossary words, filler words, routing, toolbox, settings keys, history notes, engine words, code comments, eval proof, plugin validate
	$(PYTHON) scripts/check_skills.py .
	$(PYTHON) scripts/check_versions.py .
	$(PYTHON) scripts/check_links.py .
	$(PYTHON) scripts/check_sizes.py .
	$(PYTHON) scripts/check_plugin.py .
	$(PYTHON) scripts/check_index.py .
	$(PYTHON) scripts/check_provenance.py .
	$(PYTHON) scripts/check_glossary.py .
	$(PYTHON) scripts/check_words.py .
	$(PYTHON) scripts/check_routing.py .
	$(PYTHON) scripts/check_toolbox.py .
	$(PYTHON) scripts/check_settings_keys.py .
	$(PYTHON) scripts/check_history.py .
	$(PYTHON) scripts/check_generic.py .
	$(PYTHON) scripts/check_comments.py .
	$(PYTHON) scripts/check_eval_proof.py .
	claude plugin validate --strict .
	for plugin in plugins/*/; do claude plugin validate --strict --profile directory $$plugin || exit 1; done

test: ## each check against its planted fixtures, the index builder and the release config
	$(PYTHON) -m unittest discover --start-directory tests --top-level-directory .

index: ## rebuild the root README's AGENTS.md block from each plugin's hooks/index.txt
	$(PYTHON) scripts/build_index.py .

size: ## changed lines and files against the pull-request size limits
	$(PYTHON) scripts/branch_size.py origin/main

help: ## list the targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-6s %s\n", $$1, $$2}'
