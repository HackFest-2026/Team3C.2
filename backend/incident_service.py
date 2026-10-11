from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .models import Incident


def create_incident(
    db: Session,
    device_id: str,
    zone: str,
    risk_score: float,
    risk_level: str,
    hazards: list[str],
) -> Incident:
    """
    Create a safety incident from a HIGH or CRITICAL risk event.
    """

    hazard_type = ", ".join(hazards) if hazards else "UNKNOWN_HAZARD"

    if risk_level == "CRITICAL":
        action_required = "EVACUATE_ZONE"
    else:
        action_required = "INSPECT_ZONE"

    incident = Incident(
        device_id=device_id,
        zone=zone,
        risk_score=risk_score,
        risk_level=risk_level,
        hazard_type=hazard_type,
        status="OPEN",
        action_required=action_required,
        created_at=datetime.now(timezone.utc),
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


def resolve_incident(
    db: Session,
    incident_id: int,
) -> Incident | None:
    """
    Mark an incident as resolved.
    """

    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        return None

    incident.status = "RESOLVED"
    incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)

    return incident