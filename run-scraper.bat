@echo off
title Scraper - scrap-carros
docker compose exec backend python -m app.services.scraper.main
pause
