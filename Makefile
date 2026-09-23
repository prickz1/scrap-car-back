.PHONY: run back build down scrape enrich enrich-detail

back:
	docker compose up -d

run: back

build:
	docker compose up --build -d

down:
	docker compose down

scrape:
	cmd.exe /c start run-scraper.bat

enrich:
	docker compose exec backend python -m app.scripts.enrichment.main

enrich-detail:
	cmd.exe /c start run-enrich-detail.bat
