import json
import logging
import time

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.core.config import Settings
from app.models.schemas import TelemetryPayload
from app.mqtt.topics import MQTT_TELEMETRY_SUBSCRIBE_TOPIC
from app.services.reading_service import ReadingService

logger = logging.getLogger(__name__)


class MQTTTelemetryClient:
    def __init__(self, settings: Settings, reading_service: ReadingService) -> None:
        self.settings = settings
        self.reading_service = reading_service
        self.connected = False
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="iot-service-consumer",
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def connect(self, attempts: int = 20, delay_seconds: float = 1.0) -> None:
        last_error: Exception | None = None
        for _ in range(attempts):
            try:
                self.client.connect(
                    self.settings.mqtt_host,
                    self.settings.mqtt_port,
                    self.settings.mqtt_keepalive,
                )
                self.client.loop_start()
                return
            except OSError as exc:
                last_error = exc
                time.sleep(delay_seconds)
        if last_error:
            raise last_error

    def disconnect(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        self.connected = reason_code == 0
        if self.connected:
            client.subscribe(MQTT_TELEMETRY_SUBSCRIBE_TOPIC)
            logger.info("Subscribed to MQTT topic %s", MQTT_TELEMETRY_SUBSCRIBE_TOPIC)
        else:
            logger.warning("MQTT connection failed: %s", reason_code)

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties) -> None:
        self.connected = False
        logger.info("MQTT disconnected: %s", reason_code)

    def _on_message(self, client, userdata, message) -> None:
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            telemetry = TelemetryPayload.model_validate(payload)
            self.reading_service.ingest_telemetry(telemetry)
        except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as exc:
            logger.warning("Invalid telemetry payload on %s: %s", message.topic, exc)
        except Exception:
            logger.exception("Failed to persist telemetry payload from %s", message.topic)
