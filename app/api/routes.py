from fastapi import APIRouter, HTTPException, Query, Request

from app.models.schemas import HealthResponse, Reading, Sensor, SimulatorState

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> dict:
    state = request.app.state
    return {
        "service": state.settings.service_name,
        "status": "ok",
        "mqtt_connected": state.mqtt_client.connected,
        "simulator_running": state.simulator.running,
    }


@router.get("/sensors", response_model=list[Sensor])
def list_sensors(request: Request) -> list[dict]:
    return request.app.state.sensor_service.list_sensors()


@router.get("/sensors/{sensor_id}", response_model=Sensor)
def get_sensor(sensor_id: str, request: Request) -> dict:
    sensor = request.app.state.sensor_service.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.get("/readings/latest", response_model=list[Reading])
def latest_readings(request: Request) -> list[dict]:
    return request.app.state.reading_service.get_latest_readings()


@router.get("/readings", response_model=list[Reading])
def sensor_readings(
    request: Request,
    sensor_id: str = Query(...),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict]:
    return request.app.state.reading_service.get_sensor_readings(sensor_id, limit)


@router.get("/zones/{zone}/readings", response_model=list[Reading])
def zone_readings(
    zone: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict]:
    return request.app.state.reading_service.get_zone_readings(zone, limit)


@router.post("/simulator/start", response_model=SimulatorState)
def start_simulator(request: Request) -> dict[str, bool]:
    request.app.state.simulator.start()
    return {"running": request.app.state.simulator.running}


@router.post("/simulator/stop", response_model=SimulatorState)
def stop_simulator(request: Request) -> dict[str, bool]:
    request.app.state.simulator.stop()
    return {"running": request.app.state.simulator.running}
