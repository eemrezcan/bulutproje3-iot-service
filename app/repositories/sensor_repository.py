from app.core.config import Settings
from app.models.schemas import Sensor
from app.repositories.dynamodb import from_dynamodb_value, to_dynamodb_value


SEED_SENSORS = [
    Sensor(
        sensor_id="sensor_meydan_01",
        zone="Meydan",
        name="Meydan Cevre Sensoru",
        status="active",
        latitude=39.9208,
        longitude=32.8541,
    ),
    Sensor(
        sensor_id="sensor_otogar_01",
        zone="Otogar",
        name="Otogar Trafik Sensoru",
        status="active",
        latitude=39.9478,
        longitude=32.8436,
    ),
    Sensor(
        sensor_id="sensor_kampus_01",
        zone="Kampus",
        name="Kampus Hava Sensoru",
        status="active",
        latitude=39.8674,
        longitude=32.7339,
    ),
    Sensor(
        sensor_id="sensor_hastane_01",
        zone="Hastane",
        name="Hastane Bolgesi Sensoru",
        status="active",
        latitude=39.9334,
        longitude=32.8597,
    ),
    Sensor(
        sensor_id="sensor_sanayi_01",
        zone="Sanayi",
        name="Sanayi Emisyon Sensoru",
        status="active",
        latitude=39.9682,
        longitude=32.7427,
    ),
]


class SensorRepository:
    def __init__(self, settings: Settings, dynamodb_resource) -> None:
        self.table = dynamodb_resource.Table(settings.sensors_table_name)

    def seed_default_sensors(self) -> None:
        with self.table.batch_writer(overwrite_by_pkeys=["sensor_id"]) as batch:
            for sensor in SEED_SENSORS:
                batch.put_item(Item=to_dynamodb_value(sensor.model_dump()))

    def list_sensors(self) -> list[dict]:
        response = self.table.scan()
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))
        return sorted((from_dynamodb_value(item) for item in items), key=lambda item: item["zone"])

    def get_sensor(self, sensor_id: str) -> dict | None:
        response = self.table.get_item(Key={"sensor_id": sensor_id})
        item = response.get("Item")
        return from_dynamodb_value(item) if item else None
