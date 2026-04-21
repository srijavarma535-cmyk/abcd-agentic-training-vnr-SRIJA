.PHONY: install run ui test pull-model

install:
	pip install -r requirements.txt

pull-model:
	ollama pull llama3.2

run:
	python main.py --startup "$(STARTUP)" --mode $(or $(MODE),full)

ui:
	streamlit run ui/app.py

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	rm -rf data/outputs/*.html data/outputs/*.json data/outputs/*.md 2>/dev/null; true
