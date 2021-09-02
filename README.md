```
.
├── README.md <--- project description
├── dev.env <--- Setting vscode development env
├── environment.yml <--- Used for creating a new conda env
├── Makefile <--- Control project lifecycle, use 'make train', 'make test', or 'make data' etc to do it
├── models <--- Store model, .pickle or .h5
├── data <--- Store data in different pipeline stages. This folder is ignored by git
│   ├── 00_raw
│   └── 01_clean
├── notebook
│   └── dnn.ipynb
├── reports <--- reports of each model's performances, and experimental condition etc
│   ├── dnn
│   └── cnn
└── src
	├── main
	|	├── __init__.py
	|	├── data <--- data pipeline script
	|	│   ├── __init__.py
	|	│   └── raw.py
	|	├── models <--- final model script, let us easy to reproduce model train/prediction by make tool
	|	│   ├── __init__.py
	|	│   ├── cnn.py
	|	│   └── dnn.py
	|	└── visulaization <--- visulaization tools for model performances, data etc
	|		└── __init__.py
	|
	└── test
	|
	└── utility
	    ├── __init__.py
	    └── logger.py
```
