.PHONY: all
all: example/main.yml example/main_example.yml

example/main.yml: example/main.yaml
	poetry run python -m tellurium --config $<

example/main_example.yml:
	poetry run python -m tellurium --emit_example $@

.PHONY: clean
clean:
	find example/ -name "*.yml" -exec rm {} +

MODULE_NAME = sample2

.PHONY: install
install:
	mv sample $(MODULE_NAME)
	sed -i '' 's/name = "sample"/name = "$(MODULE_NAME)"/g' pyproject.toml
	sed -i '' 's/from sample import square/from $(MODULE_NAME) import square/g' tests/test_square.py
	poetry install
