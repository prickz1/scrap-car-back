.PHONY: back build down scrape enrich enrich-detail clean-scrap treinar treinar-popular

back:
	docker compose up -d

build:
	docker compose up --build -d

down:
	docker compose down

scrape:
	cmd.exe /c start run-scraper.bat

enrich:
	docker compose exec backend python -m app.scripts.enrichment.detail.main

enrich-detail:
	cmd.exe /c start run-enrich-detail.bat

clean-scrap:
	docker compose exec postgres psql -U paulo -d scrap_carros -c "DELETE FROM cars WHERE marca = 'ERRO' AND quilometragem IS NULL;"

treinar:
	cd treino && py -3.14 treinar_gb.py

treinar-popular:
	cd treino && py -3.14 treinar_gb_popular.py
