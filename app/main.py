import os

from fastapi import FastAPI

app = FastAPI(title="IoT Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "service": os.getenv("SERVICE_NAME", "iot-service"),
        "status": "ok",
    }

