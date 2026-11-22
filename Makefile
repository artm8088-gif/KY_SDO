.PHONY: help install test run run-all run-network run-education run-warehouse clean

PYTHON = python3
SRC_DIR = src
EXAMPLES_DIR = examples

help:
	@echo "Доступные команды:"
	@echo "  make install         - Установить зависимости"
	@echo "  make test            - Запустить тесты"
	@echo "  make run-all         - Запустить транслятор для ВСЕХ трех примеров"
	@echo "  make run-network     - Запустить транслятор для examples/network.conf"
	@echo "  make run-education   - Запустить транслятор для examples/education.conf"
	@echo "  make run-warehouse   - Запустить транслятор для examples/warehouse.conf"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -v tests/

run-network:
	$(PYTHON) -m $(SRC_DIR).main -i $(EXAMPLES_DIR)/network.conf -o network_output.json
	@echo "Результат сохранен в network_output.json"

run-education:
	$(PYTHON) -m $(SRC_DIR).main -i $(EXAMPLES_DIR)/education.conf -o education_output.json
	@echo "Результат сохранен в education_output.json"

run-warehouse:
	$(PYTHON) -m $(SRC_DIR).main -i $(EXAMPLES_DIR)/warehouse.conf -o warehouse_output.json
	@echo "Результат сохранен в warehouse_output.json"

run-all: run-network run-education run-warehouse
	@echo "Все три примера успешно скомпилированы!"
