"""
Simple, defensively-written math utilities. Deliberately minimal --
built as a verified-clean baseline for measuring false-positive rate.
"""


def safe_divide(numerator: float, denominator: float) -> float | None:
    """Returns None instead of raising when dividing by zero."""
    if denominator == 0:
        return None
    return numerator / denominator


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Constrains value to the [minimum, maximum] range."""
    if minimum > maximum:
        raise ValueError("minimum must not exceed maximum")
    return max(minimum, min(value, maximum))


def average(numbers: list[float]) -> float | None:
    """Returns None for an empty list instead of raising."""
    if not numbers:
        return None
    return sum(numbers) / len(numbers)