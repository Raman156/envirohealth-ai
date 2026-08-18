from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


def aggregate_symptoms(reports: List[Any]) -> Dict[str, int]:
    """Count symptom occurrences from list of health reports."""
    counts = defaultdict(int)
    for report in reports:
        if hasattr(report, "symptoms") and report.symptoms:
            for symptom in report.symptoms:
                counts[symptom] += 1
    return dict(counts)


def aggregate_env_readings(readings: List[Any]) -> Dict[str, float]:
    """Average environmental readings by parameter."""
    sums = defaultdict(float)
    counts = defaultdict(int)
    for r in readings:
        sums[r.parameter] += r.value
        counts[r.parameter] += 1
    return {param: sums[param] / counts[param] for param in sums}


def get_period_bounds(period: str) -> tuple:
    """Return (start, end) datetime for period string."""
    now = datetime.utcnow()
    periods = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
        "180d": timedelta(days=180),
        "1y": timedelta(days=365),
    }
    delta = periods.get(period, timedelta(days=30))
    return (now - delta, now)
