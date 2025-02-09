.PHONY: all
all: output_dump_myself.yaml output_dump_myself_example.yaml output_plot_data.png make

output_dump_myself.yaml: dump_myself.yaml dump_myself.py
	python dump_myself.py --config dump_myself.yaml

output_dump_myself_example.yaml: dump_myself.py
	python dump_myself.py --emit_example output_dump_myself_example.yaml

output_plot_data.png: plot_data.yaml plot_data.py
	python plot_data.py --config plot_data.yaml

.PHONY: make
make: make.yaml ../tellurium/make.py
	python -m tellurium.make --config make.yaml

.PHONY: clean
clean:
	find ./ -name "output*" -exec rm {} +
