.PHONY: dev build test lint install build-dataset

install:
	pip install -e ".[api,ml,dev]"
	npm install

dev:
	turbo dev

build:
	turbo build

test:
	turbo test

lint:
	turbo lint

build-dataset:
	python -m ml.data.build_dataset

api-dev:
	cd apps/api && uvicorn main:app --reload --port 8000

api-test:
	pytest apps/api/tests -v --cov=apps/api --cov-report=html

ml-test:
	pytest ml/ -v --cov=ml --cov-report=html
