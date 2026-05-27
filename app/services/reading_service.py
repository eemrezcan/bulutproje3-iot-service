from app.models.schemas import Reading, StatusLevel, TelemetryPayload
from app.repositories.reading_repository import ReadingRepository
from app.repositories.sensor_repository import SensorRepository


def calculate_status_level(payload: TelemetryPayload) -> StatusLevel:
    if (
        payload.air_quality_index >= 150
        or payload.traffic_level >= 85
        or payload.temperature >= 38
    ):
        return "critical"
    if (
        payload.air_quality_index >= 100
        or payload.traffic_level >= 65
        or payload.temperature >= 34
    ):
        return "warning"
    return "normal"


class ReadingService:
    def __init__(
        self,
        reading_repository: ReadingRepository,
        sensor_repository: SensorRepository,
    ) -> None:
        self.reading_repository = reading_repository
        self.sensor_repository = sensor_repository

    def ingest_telemetry(self, payload: TelemetryPayload) -> Reading:
        reading = Reading(**payload.model_dump(), status_level=calculate_status_level(payload))
        self.reading_repository.save_reading(reading)
        return reading

    def get_latest_readings(self) -> list[dict]:
        sensors = self.sensor_repository.list_sensors()
        return self.reading_repository.latest_by_sensors([sensor["sensor_id"] for sensor in sensors])

    def get_sensor_readings(self, sensor_id: str, limit: int) -> list[dict]:
        return self.reading_repository.list_by_sensor(sensor_id, limit=limit)

    def get_zone_readings(self, zone: str, limit: int) -> list[dict]:
        return self.reading_repository.list_by_zone(zone, limit=limit)
