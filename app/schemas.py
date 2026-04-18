from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReadingRequest(BaseModel):
    sensor_id: str
    value: float
    unit: str = Field(..., description="fahrenheit | celsius | volts | psi | percent | mm/s")
    tags: List[str] = []
    correlation_id: str = ""


class ReadingResponse(BaseModel):
    sensor_id: str
    value: float
    unit: str
    status: str
    timestamp: datetime
    correlation_id: str
    tags: List[str]
    metadata: Dict[str, Any]


class BatchRequest(BaseModel):
    readings: List[ReadingRequest]


class BatchResponse(BaseModel):
    total_processed: int
    valid_count: int
    anomaly_count: int
    invalid_count: int
    success_rate: float
    errors: List[str]


class StatsResponse(BaseModel):
    sensor_id: str
    count: int
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    anomaly_count: int
    period_start: Optional[datetime]
    period_end: Optional[datetime]


class ThresholdRequest(BaseModel):
    sensor_id: str
    min_value: float
    max_value: float
    unit: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
