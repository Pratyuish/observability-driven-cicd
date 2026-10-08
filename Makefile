PYTHON ?= python3

.PHONY: help validate test demo demo-down traffic bad-traffic precheck mock-agent clean

help:
	@echo "Targets:"
	@echo "  make demo         Start kind + demo API + OTel Collector + Prometheus + Grafana"
	@echo "  make demo-down    Stop port-forwards and delete the local kind cluster"
	@echo "  make traffic      Generate healthy demo traffic"
	@echo "  make bad-traffic  Inject intentional latency and HTTP 500 responses"
	@echo "  make precheck     Run the pre-deployment Kubernetes health check"
	@echo "  make validate     Compile Python and validate required files"
	@echo "  make test         Run unit tests"
	@echo "  make mock-agent   Run the deterministic agent against sample health data"
	@echo "  make clean        Remove local reports and Python cache"

demo:
	bash scripts/demo.sh

demo-down:
	bash scripts/demo_down.sh

traffic:
	bash scripts/traffic.sh good

bad-traffic:
	bash scripts/traffic.sh bad

precheck:
	$(PYTHON) scripts/pre_deploy_health.py

validate:
	$(PYTHON) -m py_compile scripts/*.py agents/*.py apps/demo-api/app.py
	test -f README.md
	test -f LICENSE
	test -f slo/slo.yaml
	test -f kubernetes/demo-stack.yaml
	test -f apps/demo-api/Dockerfile

test:
	$(PYTHON) -m unittest discover -s tests -v

mock-agent:
	$(PYTHON) agents/mock_reliability_agent.py examples/health-report-pass.json

clean:
	rm -rf reports .demo-pids __pycache__ scripts/__pycache__ agents/__pycache__ tests/__pycache__ apps/demo-api/__pycache__
