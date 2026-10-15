# Energy weather hub

A typed Python pipeline that explains how weather drives Germany's electricity grid. It pulls hourly station weather from the Deutscher Wetterdienst (DWD) and grid load / renewable generation / day-ahead price from SMARD (Bundesnetzagentur), cleans both, and will serve the result through an async FastAPI backend on top of PostgreSQL.

Both sources are deliberately messy: DWD's station list is a fixed-width Latin-1 text file that breaks naive parsers, and SMARD revises its own recent values after publication. Handling that correctly, not wrapping a clean REST API, is the point of this project.

## Status

- [x] **Step 1** — Project skeleton (`uv` package, console-script entry point)
- [x] **Step 2** — DWD weather parsed and downloaded (`dwd.py`)
- [x] **Step 3** — SMARD electricity data fetched (`smard.py`)
- [ ] Step 4 — Nearest-station matching (haversine, own algorithm)
- [ ] Step 5 — Validate and clean with Pydantic, compute statistics
- [ ] Step 6 — Charts (temperature vs. load, renewable share, price distribution)
- [ ] Step 7 — PostgreSQL schema + 5 analytics queries
- [ ] Step 8 — Postgres in Docker + idempotent loader
- [ ] Step 9 — Async FastAPI service
- [ ] Step 10 — Dockerise the full stack
- [ ] Step 11 — CI pipeline and tests

## What works right now

- `dwd.py` downloads the DWD station list (fixed-width, Latin-1), parses it field by field — handling multi-word station names and the 16 stations with no federal state — then downloads and cleans hourly temperature data for 15 stations. Running it produces `stations.csv` (668 stations) and `hourly_temperature.csv` (~198k hourly readings, UTC timestamps).
- `smard.py` fetches the last 5 weeks of national grid load, wind onshore generation, solar generation, and the day-ahead price from SMARD's weekly JSON chunks. Timestamps are stored in UTC with a derived Europe/Berlin column for display; hours that are not yet published are kept as missing values, not dropped. Running it produces `smard_data.csv` (~3,360 rows across the 4 series).

## Project structure

```
energy-weather-hub/
├── .env.example
├── docker-compose.yml          # Step 8/10
├── Dockerfile                  # Step 8/10
├── .github/workflows/ci.yml    # Step 11
├── sql/
│   ├── schema.sql              # Step 7
│   └── queries/                # Step 7
├── charts/                     # Step 6
├── src/energy_weather_hub/
│   ├── dwd.py                  # done
│   ├── smard.py                # done
│   ├── nearest.py              # Step 4
│   ├── models.py                # Step 5
│   ├── clean.py                  # Step 5
│   ├── charts.py                 # Step 6
│   ├── db.py                     # Step 8/9
│   ├── loader.py                 # Step 8
│   └── api.py                    # Step 9
└── tests/
    ├── test_dwd_parse.py
    ├── test_dst.py
    └── test_idempotent.py
```

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Running what exists so far

Both pipelines write their output into the folder they're run from, so run them from inside the package folder:

```bash
cd src/energy_weather_hub
uv run python dwd.py      # -> stations.csv, hourly_temperature.csv
uv run python smard.py    # -> smard_data.csv
```

## Data sources

- [DWD open data](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/) — hourly station weather, free and public.
- [SMARD](https://www.smard.de/home/downloadcenter/download-marktdaten/) / [community API docs](https://smard.api.bund.dev/) — electricity load, generation and price, free and public.

## Tech stack

Python 3.12, uv, requests, pandas, NumPy, FastAPI, Uvicorn, psycopg (async), PostgreSQL 16, Docker Compose, GitHub Actions.
