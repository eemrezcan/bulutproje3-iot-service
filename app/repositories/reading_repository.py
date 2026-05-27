from boto3.dynamodb.conditions import Key

from app.core.config import Settings
from app.models.schemas import Reading
from app.repositories.dynamodb import from_dynamodb_value, to_dynamodb_value


class ReadingRepository:
    def __init__(self, settings: Settings, dynamodb_resource) -> None:
        self.settings = settings
        self.table = dynamodb_resource.Table(settings.readings_table_name)

    def save_reading(self, reading: Reading) -> None:
        self.table.put_item(Item=to_dynamodb_value(reading.model_dump()))

    def list_by_sensor(self, sensor_id: str, limit: int = 50) -> list[dict]:
        response = self.table.query(
            KeyConditionExpression=Key("sensor_id").eq(sensor_id),
            ScanIndexForward=False,
            Limit=limit,
        )
        return [from_dynamodb_value(item) for item in response.get("Items", [])]

    def list_by_zone(self, zone: str, limit: int = 50) -> list[dict]:
        response = self.table.query(
            IndexName=self.settings.zone_timestamp_index_name,
            KeyConditionExpression=Key("zone").eq(zone),
            ScanIndexForward=False,
            Limit=limit,
        )
        return [from_dynamodb_value(item) for item in response.get("Items", [])]

    def latest_by_sensors(self, sensor_ids: list[str]) -> list[dict]:
        latest = []
        for sensor_id in sensor_ids:
            readings = self.list_by_sensor(sensor_id, limit=1)
            if readings:
                latest.append(readings[0])
        return sorted(latest, key=lambda item: item["zone"])
