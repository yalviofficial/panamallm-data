.PHONY: setup validate clean download

setup:
	pip install -r scripts/requirements.txt
	python scripts/setup.py

validate:
	python scripts/validate_contrib.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

download:
	python scripts/download_sources.py
