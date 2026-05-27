from typing import Literal

from pydantic import BaseModel, Field


StatusLevel = Literal["normal", "warning", "critical"]


class Sensor(BaseModel):
    sensor_id: str
    zone: str
    name: str
    status: str
    latitude: float
    longitude: float


class TelemetryPayload(BaseModel):
    sensor_id: str
    zone: str
    temperature: float
    humidity: int
    air_quality_index: int
    traffic_level: int
    timestamp: str


class Reading(TelemetryPayload):
    status_level: StatusLevel


class HealthResponse(BaseModel):
    service: str
    status: str
    mqtt_connected: bool
    simulator_running: bool


class SimulatorState(BaseModel):
    running: bool = Field(description="Whether the simulator worker is publishing telemetry")
