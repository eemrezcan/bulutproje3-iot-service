MQTT_TELEMETRY_SUBSCRIBE_TOPIC = "smart-city/iot/+/+/telemetry"


def zone_slug(zone: str) -> str:
    return zone.strip().lower().replace(" ", "-")


def telemetry_topic(zone: str, sensor_id: str) -> str:
    return f"smart-city/iot/{zone_slug(zone)}/{sensor_id}/telemetry"
