.PHONY: run back build down scrape

back:
	docker compose up -d

run: back

build:
	docker compose up --build -d

down:
	docker compose down

scrape:
	cmd.exe /c start run-scraper.bat
