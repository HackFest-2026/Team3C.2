from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from .database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(String, nullable=False, index=True)
    zone = Column(String, nullable=False, index=True)

    gas = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(String, nullable=False, index=True)
    zone = Column(String, nullable=False, index=True)

    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False, index=True)

    hazard_type = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="OPEN",
        index=True,
    )

    action_required = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    resolved_at = Column(
        DateTime,
        nullable=True,
    )