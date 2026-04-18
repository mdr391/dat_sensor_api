from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from dat_service_lib import (
    SensorReading, SensorUnit, SensorThreshold,
    SensorService, InMemoryThresholdRepo,
    SensorError, generate_correlation_id,
)
from app.dependencies import get_service, get_threshold_repo
from app.schemas import (
    ReadingRequest, ReadingResponse,
    BatchRequest, BatchResponse,
    StatsResponse, ThresholdRequest,
)

router = APIRouter(prefix="/sensors", tags=["sensors"])


def _to_response(r: SensorReading) -> ReadingResponse:
    return ReadingResponse(
        sensor_id=r.sensor_id,
        value=r.value,
        unit=r.unit.value,
        status=r.status.value,
        timestamp=r.timestamp,
        correlation_id=r.correlation_id,
        tags=r.tags,
        metadata=r.metadata,
    )


def _to_domain(req: ReadingRequest) -> SensorReading:
    try:
        unit = SensorUnit(req.unit)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unknown unit: {req.unit}")
    return SensorReading(
        sensor_id=req.sensor_id,
        value=req.value,
        unit=unit,
        tags=req.tags,
        correlation_id=req.correlation_id or generate_correlation_id(),
    )


@router.post("/readings", response_model=ReadingResponse, status_code=201)
def submit_reading(
    body: ReadingRequest,
    service: SensorService = Depends(get_service),
):
    """Submit a single sensor reading. Returns the processed result with status."""
    try:
        result = service.process_reading(_to_domain(body))
        return _to_response(result)
    except SensorError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/readings/batch", response_model=BatchResponse)
def submit_batch(
    body: BatchRequest,
    service: SensorService = Depends(get_service),
):
    """Submit a batch of readings. Errors are isolated — one bad reading won't fail the batch."""
    readings = [_to_domain(r) for r in body.readings]
    result = service.process_batch(readings)
    return BatchResponse(
        total_processed=result.total_processed,
        valid_count=result.valid_count,
        anomaly_count=result.anomaly_count,
        invalid_count=result.invalid_count,
        success_rate=result.success_rate,
        errors=result.errors,
    )


@router.get("/{sensor_id}/latest", response_model=ReadingResponse)
def get_latest(
    sensor_id: str,
    service: SensorService = Depends(get_service),
):
    """Get the most recent reading for a sensor."""
    reading = service.get_latest_reading(sensor_id)
    if not reading:
        raise HTTPException(status_code=404, detail=f"No readings found for {sensor_id}")
    return _to_response(reading)


@router.get("/{sensor_id}/stats", response_model=StatsResponse)
def get_stats(
    sensor_id: str,
    hours: int = Query(default=24, ge=1, le=168),
    service: SensorService = Depends(get_service),
):
    """Get aggregated stats for a sensor over the last N hours (default 24, max 168)."""
    stats = service.get_sensor_stats(sensor_id, hours=hours)
    if not stats:
        raise HTTPException(status_code=404, detail=f"No data for {sensor_id}")
    return StatsResponse(
        sensor_id=stats.sensor_id,
        count=stats.count,
        mean=stats.mean,
        std_dev=stats.std_dev,
        min_value=stats.min_value,
        max_value=stats.max_value,
        anomaly_count=stats.anomaly_count,
        period_start=stats.period_start,
        period_end=stats.period_end,
    )


@router.get("/{sensor_id}/history", response_model=List[ReadingResponse])
def get_history(
    sensor_id: str,
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=1000),
    service: SensorService = Depends(get_service),
):
    """Get reading history for a sensor."""
    readings = service.get_readings_history(sensor_id, hours=hours, limit=limit)
    if not readings:
        raise HTTPException(status_code=404, detail=f"No history for {sensor_id}")
    return [_to_response(r) for r in readings]


@router.post("/thresholds", status_code=201)
def set_threshold(
    body: ThresholdRequest,
    threshold_repo: InMemoryThresholdRepo = Depends(get_threshold_repo),
):
    """Configure alert thresholds for a sensor."""
    try:
        unit = SensorUnit(body.unit)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unknown unit: {body.unit}")
    threshold_repo.save_threshold(
        SensorThreshold(
            sensor_id=body.sensor_id,
            min_value=body.min_value,
            max_value=body.max_value,
            unit=unit,
        )
    )
    return {"message": f"Threshold set for {body.sensor_id}"}
