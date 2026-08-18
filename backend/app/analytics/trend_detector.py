from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class TrendItem:
    condition: str
    current: int
    previous: int
    change_percent: float
    direction: str


def calculate_trend(current: int, previous: int) -> Tuple[float, str]:
    """Returns (change_percent, direction)."""
    if previous == 0:
        if current > 0:
            return (100.0, "INCREASING")
        return (0.0, "STABLE")

    change = ((current - previous) / previous) * 100

    if change > 10:
        direction = "INCREASING"
    elif change < -10:
        direction = "DECREASING"
    else:
        direction = "STABLE"

    return (round(change, 1), direction)


def build_symptom_trends(
    current_counts: Dict[str, int],
    previous_counts: Dict[str, int],
) -> List[TrendItem]:
    all_symptoms = set(list(current_counts.keys()) + list(previous_counts.keys()))
    trends = []

    for symptom in all_symptoms:
        current = current_counts.get(symptom, 0)
        previous = previous_counts.get(symptom, 0)
        change_pct, direction = calculate_trend(current, previous)
        trends.append(TrendItem(
            condition=symptom,
            current=current,
            previous=previous,
            change_percent=change_pct,
            direction=direction,
        ))

    # Sort by absolute change descending
    trends.sort(key=lambda x: abs(x.change_percent), reverse=True)
    return trends


def build_env_trends(
    current_readings: Dict[str, float],
    previous_readings: Dict[str, float],
) -> Dict[str, Tuple[float, str]]:
    """Returns dict of parameter -> (change_percent, direction)."""
    result = {}
    all_params = set(list(current_readings.keys()) + list(previous_readings.keys()))
    for param in all_params:
        curr = current_readings.get(param, 0)
        prev = previous_readings.get(param, 0)
        change, direction = calculate_trend(int(curr * 10), int(prev * 10))
        result[param] = (change, direction)
    return result
