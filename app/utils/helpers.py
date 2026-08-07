import uuid
import math
from datetime import datetime, timezone
from typing import Any


def generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())


def sanitize_string(s: str | None) -> str | None:
    """Sanitize a string by stripping leading/trailing whitespace."""
    if s is None:
        return None
    return s.strip()


def truncate_string(s: str, max_length: int = 500) -> str:
    """Truncate a string to a maximum length."""
    if len(s) > max_length:
        return s[: max_length - 3] + "..."
    return s


def parse_opening_hours(hours_data: dict | None) -> dict | None:
    """Parse and normalize opening hours data."""
    if not hours_data:
        return None
    return hours_data


def build_google_maps_url(place_id: str) -> str:
    """Build a Google Maps URL for a given place ID."""
    return f"https://www.google.com/maps/search/?api=1&query={place_id}&query_place_id={place_id}"


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate the distance between two geographical points using the haversine formula."""
    r = 6371000  # Radius of earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (math.sin(delta_phi / 2) ** 2) + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to a float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to an integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def chunk_list(lst: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of the given size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def now_utc() -> datetime:
    """Return the current time in UTC."""
    return datetime.now(timezone.utc)
