.PHONY: back build down scrape enrich enrich-detail clean-scrap treinar treinar-popular treinar-clf-gb treinar-economico treinar-medio treinar-premium

back:
	docker compose up -d

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

treinar:
	cd treino && py -3.14 treinar_gb.py

treinar-popular:
	cd treino && py -3.14 treinar_gb_popular.py

treinar-clf-gb:
	cd treino && py -3.14 treinar_classificador_gb.py

treinar-economico:
	cd treino && py -3.14 treinar_gb_economico.py

treinar-medio:
	cd treino && py -3.14 treinar_gb_medio.py

treinar-premium:
	cd treino && py -3.14 treinar_gb_premium.py
