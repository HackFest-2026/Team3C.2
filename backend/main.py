from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .incident_service import create_incident, resolve_incident
from .models import Incident, SensorReading

from edge.risk_engine import calculate_risk
from edge.recommendation_engine import generate_recommendation


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Mine Safety Intelligence API",
    description="Backend for the Hackfest mining safety system",
    version="1.0.0",
)


class SensorData(BaseModel):
    device_id: str
    zone: str
    gas: float = Field(ge=0)
    temperature: float
    distance: float = Field(ge=0)
    vibration: float = Field(ge=0)
    timestamp: datetime | None = None


@app.get("/")
def root():
    return {
        "system": "Mine Safety Intelligence",
        "status": "online",
        "message": "Backend is running",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/sensor-data")
def receive_sensor_data(
    data: SensorData,
    db: Session = Depends(get_db),
):
    # 1. Calculate risk
    risk = calculate_risk(
        gas=data.gas,
        temperature=data.temperature,
        distance=data.distance,
        vibration=data.vibration,
    )

    # 2. Generate recommendation
    recommendation = generate_recommendation(
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        hazards=risk["hazards"],
        zone=data.zone,
        gas=data.gas,
        temperature=data.temperature,
        distance=data.distance,
        vibration=data.vibration,
    )

    # 3. Store sensor reading
    reading = SensorReading(
        device_id=data.device_id,
        zone=data.zone,
        gas=data.gas,
        temperature=data.temperature,
        distance=data.distance,
        vibration=data.vibration,
        timestamp=data.timestamp or datetime.now(timezone.utc),
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    # 4. Create incident for HIGH / CRITICAL
    incident = None

    if risk["risk_level"] in ["HIGH", "CRITICAL"]:
        incident = create_incident(
            db=db,
            device_id=data.device_id,
            zone=data.zone,
            risk_score=risk["risk_score"],
            risk_level=risk["risk_level"],
            hazards=risk["hazards"],
        )

    return {
        "status": "received",
        "message": "Sensor reading processed successfully",
        "reading_id": reading.id,

        "data": {
            "device_id": reading.device_id,
            "zone": reading.zone,
            "gas": reading.gas,
            "temperature": reading.temperature,
            "distance": reading.distance,
            "vibration": reading.vibration,
            "timestamp": reading.timestamp.isoformat(),
        },

        "risk": risk,

        "recommendation": recommendation,

        "incident": (
            {
                "id": incident.id,
                "status": incident.status,
                "risk_level": incident.risk_level,
                "risk_score": incident.risk_score,
                "hazard_type": incident.hazard_type,
                "action_required": incident.action_required,
                "created_at": incident.created_at.isoformat(),
            }
            if incident
            else None
        ),
    }


@app.get("/api/sensor-readings")
def get_sensor_readings(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    readings = (
        db.query(SensorReading)
        .order_by(SensorReading.id.desc())
        .limit(limit)
        .all()
    )

    return {
        "count": len(readings),
        "readings": [
            {
                "id": reading.id,
                "device_id": reading.device_id,
                "zone": reading.zone,
                "gas": reading.gas,
                "temperature": reading.temperature,
                "distance": reading.distance,
                "vibration": reading.vibration,
                "timestamp": reading.timestamp.isoformat(),
            }
            for reading in readings
        ],
    }


@app.get("/api/incidents")
def get_incidents(
    status: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Incident)

    if status:
        query = query.filter(
            Incident.status == status.upper()
        )

    incidents = (
        query
        .order_by(Incident.id.desc())
        .limit(limit)
        .all()
    )

    return {
        "count": len(incidents),
        "incidents": [
            {
                "id": incident.id,
                "device_id": incident.device_id,
                "zone": incident.zone,
                "risk_score": incident.risk_score,
                "risk_level": incident.risk_level,
                "hazard_type": incident.hazard_type,
                "status": incident.status,
                "action_required": incident.action_required,
                "created_at": incident.created_at.isoformat(),
                "resolved_at": (
                    incident.resolved_at.isoformat()
                    if incident.resolved_at
                    else None
                ),
            }
            for incident in incidents
        ],
    }


@app.get("/api/incidents/{incident_id}")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return {
        "id": incident.id,
        "device_id": incident.device_id,
        "zone": incident.zone,
        "risk_score": incident.risk_score,
        "risk_level": incident.risk_level,
        "hazard_type": incident.hazard_type,
        "status": incident.status,
        "action_required": incident.action_required,
        "created_at": incident.created_at.isoformat(),
        "resolved_at": (
            incident.resolved_at.isoformat()
            if incident.resolved_at
            else None
        ),
    }


@app.post("/api/incidents/{incident_id}/resolve")
def resolve_incident_endpoint(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = resolve_incident(
        db=db,
        incident_id=incident_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return {
        "status": "resolved",
        "message": "Incident resolved successfully",
        "incident": {
            "id": incident.id,
            "status": incident.status,
            "resolved_at": incident.resolved_at.isoformat(),
        },
    }


# ============================================================
# DASHBOARD API
# ============================================================

@app.get("/api/dashboard")
def get_dashboard_data(
    db: Session = Depends(get_db),
):
    # Get latest reading
    latest_reading = (
        db.query(SensorReading)
        .order_by(SensorReading.id.desc())
        .first()
    )

    # No sensor data yet
    if latest_reading is None:
        return {
            "system": {
                "status": "ONLINE",
                "message": "Waiting for sensor data",
            },
            "latest_sensor": None,
            "risk": {
                "risk_score": 0,
                "risk_level": "LOW",
                "hazards": [],
                "sensor_risks": {},
            },
            "recommendation": {
                "priority": "NORMAL",
                "action": "WAITING FOR SENSOR DATA",
                "reason": "No sensor readings have been received yet.",
                "additional_actions": [
                    "Start the sensor simulator or connect the ESP32"
                ],
            },
            "active_incidents": [],
            "recent_readings": [],
        }

    # Recalculate risk from latest reading
    risk = calculate_risk(
        gas=latest_reading.gas,
        temperature=latest_reading.temperature,
        distance=latest_reading.distance,
        vibration=latest_reading.vibration,
    )

    # Generate recommendation
    recommendation = generate_recommendation(
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        hazards=risk["hazards"],
        zone=latest_reading.zone,
        gas=latest_reading.gas,
        temperature=latest_reading.temperature,
        distance=latest_reading.distance,
        vibration=latest_reading.vibration,
    )

    # Active incidents
    active_incidents = (
        db.query(Incident)
        .filter(Incident.status == "OPEN")
        .order_by(Incident.id.desc())
        .limit(20)
        .all()
    )

    # Recent readings
    recent_readings = (
        db.query(SensorReading)
        .order_by(SensorReading.id.desc())
        .limit(20)
        .all()
    )

    return {
        "system": {
            "status": "ONLINE",
        },

        "latest_sensor": {
            "id": latest_reading.id,
            "device_id": latest_reading.device_id,
            "zone": latest_reading.zone,
            "gas": latest_reading.gas,
            "temperature": latest_reading.temperature,
            "distance": latest_reading.distance,
            "vibration": latest_reading.vibration,
            "timestamp": latest_reading.timestamp.isoformat(),
        },

        "risk": risk,

        "recommendation": recommendation,

        "active_incidents": [
            {
                "id": incident.id,
                "device_id": incident.device_id,
                "zone": incident.zone,
                "risk_score": incident.risk_score,
                "risk_level": incident.risk_level,
                "hazard_type": incident.hazard_type,
                "status": incident.status,
                "action_required": incident.action_required,
                "created_at": incident.created_at.isoformat(),
            }
            for incident in active_incidents
        ],

        "recent_readings": [
            {
                "id": reading.id,
                "device_id": reading.device_id,
                "zone": reading.zone,
                "gas": reading.gas,
                "temperature": reading.temperature,
                "distance": reading.distance,
                "vibration": reading.vibration,
                "timestamp": reading.timestamp.isoformat(),
            }
            for reading in recent_readings
        ],
    }


# ============================================================
# DASHBOARD WEBSITE
# ============================================================

app.mount(
    "/dashboard",
    StaticFiles(
        directory="dashboard",
        html=True,
    ),
    name="dashboard",
)