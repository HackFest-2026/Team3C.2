from typing import Dict, List


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Keep a value within the specified range."""
    return max(minimum, min(value, maximum))


def gas_risk(gas: float) -> float:
    """
    Prototype gas-risk scoring.

    These thresholds are demonstration assumptions for the hackathon,
    not mining safety standards.
    """
    if gas <= 300:
        return 0

    if gas <= 600:
        return ((gas - 300) / 300) * 40

    if gas <= 800:
        return 40 + ((gas - 600) / 200) * 30

    return 70 + ((min(gas, 1000) - 800) / 200) * 30


def temperature_risk(temperature: float) -> float:
    """Prototype temperature-risk scoring."""
    if temperature <= 35:
        return 0

    if temperature <= 45:
        return ((temperature - 35) / 10) * 40

    if temperature <= 55:
        return 40 + ((temperature - 45) / 10) * 30

    return 70 + ((min(temperature, 70) - 55) / 15) * 30


def distance_risk(distance: float) -> float:
    """
    Smaller distance indicates a potentially dangerous obstruction
    or structural movement.
    """
    if distance >= 60:
        return 0

    if distance >= 30:
        return ((60 - distance) / 30) * 40

    if distance >= 15:
        return 40 + ((30 - distance) / 15) * 30

    return 70 + ((15 - max(distance, 0)) / 15) * 30


def vibration_risk(vibration: float) -> float:
    """Prototype vibration-risk scoring."""
    if vibration <= 20:
        return 0

    if vibration <= 50:
        return ((vibration - 20) / 30) * 40

    if vibration <= 70:
        return 40 + ((vibration - 50) / 20) * 30

    return 70 + ((min(vibration, 100) - 70) / 30) * 30


def detect_hazards(
    gas: float,
    temperature: float,
    distance: float,
    vibration: float,
) -> List[str]:
    """Identify the hazards contributing to the risk."""

    hazards = []

    if gas > 600:
        hazards.append("HIGH_GAS_LEVEL")
    elif gas > 300:
        hazards.append("ELEVATED_GAS_LEVEL")

    if temperature > 45:
        hazards.append("HIGH_TEMPERATURE")
    elif temperature > 35:
        hazards.append("ELEVATED_TEMPERATURE")

    if distance < 30:
        hazards.append("STRUCTURAL_PROXIMITY")

    if vibration > 50:
        hazards.append("HIGH_VIBRATION")

    return hazards


def calculate_risk(
    gas: float,
    temperature: float,
    distance: float,
    vibration: float,
) -> Dict:
    """
    Calculate the overall mine safety risk.

    Weighting:
        Gas          40%
        Temperature  20%
        Distance     20%
        Vibration    20%
    """

    gas_score = clamp(gas_risk(gas))
    temperature_score = clamp(temperature_risk(temperature))
    distance_score = clamp(distance_risk(distance))
    vibration_score = clamp(vibration_risk(vibration))

    overall_score = (
        gas_score * 0.40
        + temperature_score * 0.20
        + distance_score * 0.20
        + vibration_score * 0.20
    )

    overall_score = round(clamp(overall_score), 2)

    if overall_score < 30:
        risk_level = "LOW"
    elif overall_score < 60:
        risk_level = "MEDIUM"
    elif overall_score < 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    hazards = detect_hazards(
        gas=gas,
        temperature=temperature,
        distance=distance,
        vibration=vibration,
    )

    return {
        "risk_score": overall_score,
        "risk_level": risk_level,
        "hazards": hazards,
        "sensor_risks": {
            "gas": round(gas_score, 2),
            "temperature": round(temperature_score, 2),
            "distance": round(distance_score, 2),
            "vibration": round(vibration_score, 2),
        },
    }