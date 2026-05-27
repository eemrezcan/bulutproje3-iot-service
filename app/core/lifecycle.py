from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.mqtt.client import MQTTTelemetryClient
from app.repositories.dynamodb import DynamoDBClient
from app.repositories.reading_repository import ReadingRepository
from app.repositories.sensor_repository import SensorRepository
from app.services.reading_service import ReadingService
from app.services.sensor_service import SensorService
from app.simulator.worker import SensorSimulatorWorker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    dynamodb = DynamoDBClient(settings)
    dynamodb.wait_until_ready()
    dynamodb.ensure_tables()

    sensor_repository = SensorRepository(settings, dynamodb.resource)
    reading_repository = ReadingRepository(settings, dynamodb.resource)
    sensor_repository.seed_default_sensors()

    sensor_service = SensorService(sensor_repository)
    reading_service = ReadingService(reading_repository, sensor_repository)
    mqtt_client = MQTTTelemetryClient(settings, reading_service)
    mqtt_client.connect()

    simulator = SensorSimulatorWorker(settings, sensor_service.list_sensors())
    if settings.simulator_autostart:
        simulator.start()

    app.state.settings = settings
    app.state.dynamodb = dynamodb
    app.state.sensor_service = sensor_service
    app.state.reading_service = reading_service
    app.state.mqtt_client = mqtt_client
    app.state.simulator = simulator

    try:
        yield
    finally:
        simulator.stop()
        mqtt_client.disconnect()
