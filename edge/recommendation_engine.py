from typing import Dict, List


def generate_recommendation(
    risk_score: float,
    risk_level: str,
    hazards: List[str],
    zone: str,
    gas: float,
    temperature: float,
    distance: float,
    vibration: float,
) -> Dict:
    """
    Generate a deterministic safety recommendation.

    This is a prototype decision-support engine for the hackathon.
    It is not a substitute for certified mine-safety procedures.
    """

    risk_level = risk_level.upper()

    if risk_level == "CRITICAL":
        action = f"EVACUATE {zone}"
        priority = "IMMEDIATE"

        reason = (
            "Multiple severe hazardous conditions have been detected. "
            "Personnel should be moved away from the affected zone "
            "while the incident is assessed."
        )

        additional_actions = [
            "Stop nearby machinery",
            "Alert mine supervisor",
            "Restrict zone access",
            "Initiate emergency response procedure",
        ]

    elif risk_level == "HIGH":
        action = f"INSPECT {zone} IMMEDIATELY"
        priority = "URGENT"

        reason = (
            "Significant hazardous conditions have been detected. "
            "The affected zone requires immediate inspection."
        )

        additional_actions = [
            "Alert mine supervisor",
            "Restrict unnecessary access",
            "Inspect affected equipment",
            "Continue continuous sensor monitoring",
        ]

    elif risk_level == "MEDIUM":
        action = f"MONITOR {zone}"
        priority = "WARNING"

        reason = (
            "Elevated sensor readings have been detected. "
            "Continue monitoring and inspect the affected area "
            "if the condition persists."
        )

        additional_actions = [
            "Increase monitoring frequency",
            "Inspect the affected zone",
            "Check nearby equipment",
        ]

    else:
        action = f"CONTINUE MONITORING {zone}"
        priority = "NORMAL"

        reason = (
            "Sensor readings are currently within the normal "
            "operating range."
        )

        additional_actions = [
            "Continue routine monitoring",
        ]

    return {
        "priority": priority,
        "action": action,
        "reason": reason,
        "additional_actions": additional_actions,
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "zone": zone,
        "hazards": hazards,
        "sensor_snapshot": {
            "gas": gas,
            "temperature": temperature,
            "distance": distance,
            "vibration": vibration,
        },
    }