.PHONY: all
all: plot_data.png make

plot_data.png: plot_data.yaml plot_data.py
	python plot_data.py --config plot_data.yaml

.PHONY: make
make: make.yaml make.py
	python make.py --config make.yaml

.PHONY: clean
clean:
	find ./ -name "output*" -exec rm {} +
