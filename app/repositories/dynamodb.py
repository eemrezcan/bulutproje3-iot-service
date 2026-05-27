import time
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from app.core.config import Settings


def to_dynamodb_value(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {key: to_dynamodb_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_dynamodb_value(item) for item in value]
    return value


def from_dynamodb_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    if isinstance(value, dict):
        return {key: from_dynamodb_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [from_dynamodb_value(item) for item in value]
    return value


class DynamoDBClient:
    def __init__(self, settings: Settings) -> None:
        kwargs = {
            "region_name": settings.aws_region,
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key,
        }
        if settings.dynamodb_endpoint_url:
            kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

        self.settings = settings
        self.resource = boto3.resource("dynamodb", **kwargs)
        self.client = boto3.client("dynamodb", **kwargs)

    def wait_until_ready(self, attempts: int = 20, delay_seconds: float = 1.0) -> None:
        self._with_retries(lambda: self.client.list_tables(), attempts, delay_seconds)

    def ensure_tables(self) -> None:
        self._ensure_sensors_table()
        self._ensure_readings_table()

    def table(self, table_name: str):
        return self.resource.Table(table_name)

    def _ensure_sensors_table(self) -> None:
        self._create_table_if_missing(
            table_name=self.settings.sensors_table_name,
            key_schema=[{"AttributeName": "sensor_id", "KeyType": "HASH"}],
            attribute_definitions=[{"AttributeName": "sensor_id", "AttributeType": "S"}],
        )

    def _ensure_readings_table(self) -> None:
        self._create_table_if_missing(
            table_name=self.settings.readings_table_name,
            key_schema=[
                {"AttributeName": "sensor_id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            attribute_definitions=[
                {"AttributeName": "sensor_id", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
                {"AttributeName": "zone", "AttributeType": "S"},
            ],
            global_secondary_indexes=[
                {
                    "IndexName": self.settings.zone_timestamp_index_name,
                    "KeySchema": [
                        {"AttributeName": "zone", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
        )

    def _create_table_if_missing(
        self,
        table_name: str,
        key_schema: list[dict[str, str]],
        attribute_definitions: list[dict[str, str]],
        global_secondary_indexes: list[dict[str, Any]] | None = None,
    ) -> None:
        try:
            self.client.describe_table(TableName=table_name)
            return
        except self.client.exceptions.ResourceNotFoundException:
            pass

        params: dict[str, Any] = {
            "TableName": table_name,
            "KeySchema": key_schema,
            "AttributeDefinitions": attribute_definitions,
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        }
        if global_secondary_indexes:
            params["GlobalSecondaryIndexes"] = global_secondary_indexes

        try:
            self.client.create_table(**params)
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "ResourceInUseException":
                raise

        self.client.get_waiter("table_exists").wait(TableName=table_name)

    @staticmethod
    def _with_retries(
        action: Callable[[], Any],
        attempts: int,
        delay_seconds: float,
    ) -> Any:
        last_error: Exception | None = None
        for _ in range(attempts):
            try:
                return action()
            except (EndpointConnectionError, ClientError) as exc:
                last_error = exc
                time.sleep(delay_seconds)
        if last_error:
            raise last_error
        return None
