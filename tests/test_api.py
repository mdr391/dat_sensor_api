import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_singletons():
    """Clear cached service between tests so state doesn't leak."""
    get_service.cache_clear()
    yield
    get_service.cache_clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_submit_valid_reading():
    # Set a threshold first
    client.post("/sensors/thresholds", json={
        "sensor_id": "TEMP-01",
        "min_value": 60.0,
        "max_value": 90.0,
        "unit": "fahrenheit",
    })

    response = client.post("/sensors/readings", json={
        "sensor_id": "TEMP-01",
        "value": 72.5,
        "unit": "fahrenheit",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["sensor_id"] == "TEMP-01"
    assert data["status"] == "valid"


def test_submit_anomaly_reading():
    # Set threshold so 95.2 is clearly above max
    client.post("/sensors/thresholds", json={
        "sensor_id": "TEMP-01",
        "min_value": 60.0,
        "max_value": 90.0,
        "unit": "fahrenheit",
    })

    response = client.post("/sensors/readings", json={
        "sensor_id": "TEMP-01",
        "value": 95.2,
        "unit": "fahrenheit",
    })

    assert response.status_code == 201
    assert response.json()["status"] == "anomaly"


def test_stats_not_found_before_readings():
    response = client.get("/sensors/UNKNOWN-99/stats")
    assert response.status_code == 404
