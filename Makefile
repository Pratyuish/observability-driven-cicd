PYTHON ?= python3

.PHONY: help validate test mock-agent clean

help:
	@echo "Targets:"
	@echo "  make validate     Compile Python and validate required files"
	@echo "  make test         Run unit tests"
	@echo "  make mock-agent   Run the deterministic agent against sample health data"
	@echo "  make clean        Remove local reports and Python cache"

validate:
	$(PYTHON) -m py_compile scripts/*.py agents/*.py
	test -f README.md
	test -f LICENSE
	test -f slo/slo.yaml

test:
	$(PYTHON) -m unittest discover -s tests -v

mock-agent:
	$(PYTHON) agents/mock_reliability_agent.py examples/health-report-pass.json

clean:
	rm -rf reports __pycache__ scripts/__pycache__ agents/__pycache__ tests/__pycache__
