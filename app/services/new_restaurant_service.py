from datetime import datetime, timezone
from app.database.models import Restaurant
from app.schemas.intelligence import NewRestaurantResult

class NewRestaurantDetectionService:
    def __init__(self) -> None:
        pass

    def calculate_new_restaurant_score(self, restaurant: Restaurant) -> NewRestaurantResult:
        """Calculates a score and determines if a restaurant is considered 'new'."""
        score = 0
        reasons = []

        now = datetime.now(timezone.utc)
        
        # Discovered date recency
        if hasattr(restaurant, 'first_seen') and restaurant.first_seen:
            days_since_discovery = (now - restaurant.first_seen.replace(tzinfo=timezone.utc)).days
            if days_since_discovery <= 1:
                score += 30
                reasons.append("Discovered today")
            elif days_since_discovery <= 7:
                score += 20
                reasons.append("Discovered this week")
            elif days_since_discovery <= 30:
                score += 10
                reasons.append("Discovered this month")

        # Review count
        reviews = restaurant.user_rating_count or 0
        if reviews < 10:
            score += 25
            reasons.append(f"Very few reviews ({reviews})")
        elif reviews < 30:
            score += 15
            reasons.append(f"Few reviews ({reviews})")
        elif reviews < 50:
            score += 10
            reasons.append(f"Low review count ({reviews})")

        # Business status
        if restaurant.business_status == 'OPERATIONAL' and reviews < 30:
            score += 15
            reasons.append("Operational but few signals")

        # Opening status
        opening_status = getattr(restaurant, 'opening_status', None)
        if opening_status == 'OPENING_SOON':
            score += 20
            reasons.append("Marked as opening soon")
        elif opening_status == 'NEWLY_OPENED':
            score += 15
            reasons.append("Marked as newly opened")

        # First seen == Last seen
        if hasattr(restaurant, 'first_seen') and hasattr(restaurant, 'last_seen') and restaurant.first_seen and restaurant.last_seen:
            if restaurant.first_seen == restaurant.last_seen:
                score += 10
                reasons.append("First time seeing this place")

        # Cap score at 100
        score = min(score, 100)
        is_new = score > 60
        confidence = score / 100.0
        reason_str = ", ".join(reasons)

        return NewRestaurantResult(
            is_new=is_new,
            confidence=confidence,
            reason=reason_str
        )
