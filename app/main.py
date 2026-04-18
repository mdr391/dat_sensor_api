from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import sensors
from app.schemas import HealthResponse

app = FastAPI(
    title="DAT Sensor API",
    description="HTTP inbound adapter for dat-service-lib. Demonstrates Hexagonal Architecture — FastAPI is just a delivery mechanism; all business logic lives in the domain layer.",
    version="0.1.0",
)

app.include_router(sensors.router)


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health():
    return HealthResponse(status="ok", service="dat-sensor-api", version="0.1.0")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
