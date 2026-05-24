.PHONY: run back build down logs

back:
	docker compose up -d

run: back

build:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f backend
