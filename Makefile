# Makefile da Locadora de Veículos (adaptação Python do requisito (j)).
# Em Python não há compilação; os alvos facilitam execução e testes.

PYTHON ?= python3

.PHONY: run test smoke demo clean help

help:
	@echo "Alvos disponíveis:"
	@echo "  make run    - inicia a aplicação (menu no terminal)"
	@echo "  make test   - roda os testes de regras de negócio"
	@echo "  make smoke  - E2E da apresentação (roda o roteiro e confere os marcos)"
	@echo "  make demo   - executa o roteiro da apresentação (saída no terminal)"
	@echo "  make clean  - apaga dados salvos e caches"

run:
	$(PYTHON) main.py

test:
	$(PYTHON) -m tests.test_regras

smoke:
	bash scripts/smoke_demo.sh

demo:
	@find data -name '*.json' -delete 2>/dev/null; true
	$(PYTHON) main.py < scripts/demo_inputs.txt
	@find data -name '*.json' -delete 2>/dev/null; true

clean:
	rm -rf data/*.json
	find . -type d -name __pycache__ -exec rm -rf {} +
