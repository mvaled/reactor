

all: install build

install:
	yarn install
	pip install --upgrade pip
	pip install -e .[dev]
	python setup.py develop

watch-js:
	node esbuild.conf.js -w

build:
	node esbuild.conf.js
	python setup.py sdist

test:
	flake8 --max-line-length=80 reactor
	py.test
