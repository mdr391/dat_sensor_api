"""
Composition Root — the only place that knows which adapters are wired.

Swap InMemoryReadingRepo → PostgresReadingRepo here and nothing else changes.
"""
from functools import lru_cache
from dat_service_lib import (
    SensorService,
    InMemoryReadingRepo, InMemoryThresholdRepo,
    LogAlertNotifier,
    PrometheusMetrics,
)

# Singletons — one instance shared across all requests
_reading_repo = InMemoryReadingRepo()
_threshold_repo = InMemoryThresholdRepo()

# To use PostgreSQL instead:
#   from dat_service_lib.adapters.persistence.postgres_repo import PostgresReadingRepo
#   _reading_repo = PostgresReadingRepo(connection_pool)


@lru_cache(maxsize=1)
def get_service() -> SensorService:
    return SensorService(
        reading_repo=_reading_repo,
        threshold_repo=_threshold_repo,
        alerter=LogAlertNotifier(),
        metrics=PrometheusMetrics(),
    )


def get_threshold_repo() -> InMemoryThresholdRepo:
    return _threshold_repo
