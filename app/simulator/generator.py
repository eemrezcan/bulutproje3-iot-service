import random
from datetime import UTC, datetime

from app.models.schemas import Sensor, TelemetryPayload


def generate_telemetry(sensor: Sensor) -> TelemetryPayload:
    zone_profiles = {
        "Meydan": {"temperature": (27, 38), "aqi": (55, 145), "traffic": (45, 88)},
        "Otogar": {"temperature": (26, 36), "aqi": (65, 160), "traffic": (55, 95)},
        "Kampus": {"temperature": (23, 33), "aqi": (30, 95), "traffic": (20, 62)},
        "Hastane": {"temperature": (25, 35), "aqi": (45, 120), "traffic": (35, 78)},
        "Sanayi": {"temperature": (28, 39), "aqi": (80, 180), "traffic": (40, 82)},
    }
    profile = zone_profiles.get(sensor.zone, zone_profiles["Meydan"])

    return TelemetryPayload(
        sensor_id=sensor.sensor_id,
        zone=sensor.zone,
        temperature=round(random.uniform(*profile["temperature"]), 1),
        humidity=random.randint(35, 75),
        air_quality_index=random.randint(*profile["aqi"]),
        traffic_level=random.randint(*profile["traffic"]),
        timestamp=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )
