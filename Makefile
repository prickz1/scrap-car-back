.PHONY: run back build down scrape enrich enrich-detail clean-scrap

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

clean-scrap:
	docker compose exec postgres psql -U paulo -d scrap_carros -c "DELETE FROM cars WHERE marca = 'ERRO' AND quilometragem IS NULL;"
