.PHONY: lint

# G10 (#37) make-lint gate: marketplace + plugin manifests, skills, agents, commands.
lint:
	claude plugin validate --strict .
	claude plugin validate --strict plugins/rulebook
