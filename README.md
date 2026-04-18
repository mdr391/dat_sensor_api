# dat-sensor-api

A thin FastAPI service that acts as the **HTTP inbound adapter** for [dat-service-lib](https://github.com/mdr391/dat_service_lib).

This companion project demonstrates Hexagonal Architecture in practice: FastAPI is purely a delivery mechanism. All validation, anomaly detection, alerting, and metrics live in the domain layer — the API layer translates HTTP ↔ domain objects and nothing more.

## Architecture Role

```
HTTP Client
    │
    ▼
FastAPI (inbound adapter)   ← this repo
    │  translates HTTP → domain objects
    ▼
SensorService (domain)      ← dat-service-lib
    │  talks only to ports
    ▼
Adapters (PostgreSQL / In-Memory / Slack / Prometheus)
```

Swap the persistence adapter from in-memory to PostgreSQL in [`app/dependencies.py`](app/dependencies.py) — zero changes anywhere else.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/sensors/thresholds` | Configure alert threshold for a sensor |
| `POST` | `/sensors/readings` | Submit a single reading |
| `POST` | `/sensors/readings/batch` | Submit a batch (errors isolated per reading) |
| `GET` | `/sensors/{id}/latest` | Latest reading for a sensor |
| `GET` | `/sensors/{id}/stats` | Aggregated stats (mean, std, anomaly count) |
| `GET` | `/sensors/{id}/history` | Reading history with time/limit filters |

## Quick Start

```bash
pip install -e ../dat_service_lib
pip install fastapi "uvicorn[standard]"

uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Example Usage

```bash
# 1. Set a threshold
curl -X POST http://localhost:8000/sensors/thresholds \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"TEMP-01","min_value":60.0,"max_value":90.0,"unit":"fahrenheit"}'

# 2. Submit a normal reading → status: valid
curl -X POST http://localhost:8000/sensors/readings \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"TEMP-01","value":72.5,"unit":"fahrenheit"}'

# 3. Submit an anomaly → status: anomaly, alert fires
curl -X POST http://localhost:8000/sensors/readings \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"TEMP-01","value":95.2,"unit":"fahrenheit"}'

# 4. Get stats
curl http://localhost:8000/sensors/TEMP-01/stats
```

## Project Structure

```
dat_sensor_api/
├── app/
│   ├── main.py          # FastAPI app + exception handlers
│   ├── dependencies.py  # Composition root — adapter wiring
│   ├── schemas.py       # Pydantic request/response models
│   └── routers/
│       └── sensors.py   # Route handlers (HTTP ↔ domain translation only)
└── requirements.txt
```
