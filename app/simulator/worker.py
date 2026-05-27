import json
import logging
import threading
import time

import paho.mqtt.client as mqtt

from app.core.config import Settings
from app.models.schemas import Sensor
from app.mqtt.topics import telemetry_topic
from app.simulator.generator import generate_telemetry

logger = logging.getLogger(__name__)


class SensorSimulatorWorker:
    def __init__(self, settings: Settings, sensors: list[dict]) -> None:
        self.settings = settings
        self.sensors = [Sensor.model_validate(sensor) for sensor in sensors]
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="iot-service-simulator",
        )

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> bool:
        if self.running:
            return False

        self._stop_event.clear()
        self._client.connect(
            self.settings.mqtt_host,
            self.settings.mqtt_port,
            self.settings.mqtt_keepalive,
        )
        self._client.loop_start()
        self._thread = threading.Thread(target=self._run, name="sensor-simulator", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> bool:
        if not self.running:
            return False

        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        self._client.loop_stop()
        self._client.disconnect()
        return True

    def _run(self) -> None:
        logger.info("Sensor simulator started with %s sensors", len(self.sensors))
        while not self._stop_event.is_set():
            for sensor in self.sensors:
                payload = generate_telemetry(sensor)
                self._client.publish(
                    telemetry_topic(sensor.zone, sensor.sensor_id),
                    json.dumps(payload.model_dump()),
                    qos=0,
                )
            self._stop_event.wait(self.settings.simulator_interval_seconds)
        logger.info("Sensor simulator stopped")
