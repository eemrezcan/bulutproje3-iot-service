from app.repositories.sensor_repository import SensorRepository


class SensorService:
    def __init__(self, sensor_repository: SensorRepository) -> None:
        self.sensor_repository = sensor_repository

    def list_sensors(self) -> list[dict]:
        return self.sensor_repository.list_sensors()

    def get_sensor(self, sensor_id: str) -> dict | None:
        return self.sensor_repository.get_sensor(sensor_id)
