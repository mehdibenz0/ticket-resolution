.PHONY: install run ui test demo-known demo-missing demo-novel up down

install:
	pip install -r requirements.txt

run:
	PYTHONPATH=src uvicorn resolution_copilot.app:app --reload

ui:
	PYTHONPATH=src streamlit run ui/app.py

test:
	PYTHONPATH=src pytest -q

demo-known:
	PYTHONPATH=src python scripts/demo_cli.py --scenario known

demo-missing:
	PYTHONPATH=src python scripts/demo_cli.py --scenario missing

demo-novel:
	PYTHONPATH=src python scripts/demo_cli.py --scenario novel

up:
	docker compose up --build

down:
	docker compose down
