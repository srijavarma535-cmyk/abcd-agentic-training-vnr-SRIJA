.PHONY: install run ui test lint clean

install:
	pip install -r requirements.txt

run:
	python main.py --startup "$(STARTUP)" --mode $(MODE)

ui:
	streamlit run ui/app.py

test:
	pytest tests/test_agents.py -v

integration:
	python tests/test_integration.py

lint:
	python -m py_compile main.py agents/*.py orchestrator/*.py tools/*.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf data/outputs/*.json data/outputs/*.md
