from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = Field(default="iot-service", alias="SERVICE_NAME")
    aws_region: str = Field(default="eu-central-1", alias="AWS_REGION")
    aws_access_key_id: str = Field(default="local", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="local", alias="AWS_SECRET_ACCESS_KEY")
    dynamodb_endpoint_url: str | None = Field(
        default="http://localhost:8000",
        alias="DYNAMODB_ENDPOINT_URL",
    )
    mqtt_host: str = Field(default="localhost", alias="MQTT_HOST")
    mqtt_port: int = Field(default=1883, alias="MQTT_PORT")
    mqtt_keepalive: int = Field(default=60, alias="MQTT_KEEPALIVE")
    simulator_interval_seconds: float = Field(default=3.0, alias="SIMULATOR_INTERVAL_SECONDS")
    simulator_autostart: bool = Field(default=True, alias="SIMULATOR_AUTOSTART")

    sensors_table_name: str = "iot_sensors"
    readings_table_name: str = "iot_sensor_readings"
    zone_timestamp_index_name: str = "zone-timestamp-index"

    model_config = SettingsConfigDict(env_file=".env", populate_by_name=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
