.PHONY: all
all: example/output.yml example/example.yml

example/output.yml: example/quick_check.yaml
	poetry run python -m tellurium --config $<

example/example.yml:
	poetry run python -m tellurium --emit_example $@

.PHONY: clean
clean:
	rm example/*.yml

MODULE_NAME = sample2

.PHONY: install
install:
	mv sample $(MODULE_NAME)
	sed -i '' 's/name = "sample"/name = "$(MODULE_NAME)"/g' pyproject.toml
	sed -i '' 's/from sample import square/from $(MODULE_NAME) import square/g' tests/test_square.py
	poetry install
