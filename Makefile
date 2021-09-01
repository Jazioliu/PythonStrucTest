.PHONY: all clean

IRIS_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
MNIST_URL = "https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz"
RAW_DATA = "data/00_raw/iris.csv"

CONDA_ENV_YML = environment.yml
ENV_NAME = mltmp

#all: env

clean:
	rm -f data/00_raw/*.npz

env:
	conda env create -f $(CONDA_ENV_YML) -n $(ENV_NAME)
	conda env config vars set PYTHONPATH=$(PWD)/src -n $(ENV_NAME)

data/00_raw/mnist.npz:
	python src/main/data/raw.py $(MNIST_URL) $@
