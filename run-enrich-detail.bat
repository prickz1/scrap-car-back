@echo off
title Enrichment Detail - scrap-carros
docker compose exec backend python -m app.scripts.enrichment.detail.main
pause
