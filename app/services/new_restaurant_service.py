from datetime import datetime
import json
from app.database.models import Restaurant
from app.schemas.intelligence import NewRestaurantResult

class NewRestaurantDetectionService:
    def __init__(self):
        pass

    def calculate_new_restaurant_score(self, restaurant: Restaurant) -> NewRestaurantResult:
        """
        Calculates a score indicating how likely a restaurant is to be newly opened.
        Assigns a categorization status based on the score and details.
        """
        score = 0.0
        confidence = 0.5
        evidence = []
        reason = "Based on available data."
        
        # 1. Review count is a strong indicator
        if restaurant.user_rating_count is not None:
            if restaurant.user_rating_count == 0:
                score += 50.0
                confidence += 0.2
                evidence.append("No reviews yet, highly likely to be new.")
            elif restaurant.user_rating_count < 10:
                score += 30.0
                confidence += 0.1
                evidence.append("Very few reviews (< 10).")
            elif restaurant.user_rating_count > 100:
                score -= 40.0
                evidence.append("High number of reviews suggests it is established.")
        else:
            score += 10.0
            evidence.append("Review count is unknown, slightly increasing likelihood.")

        # 2. Business status
        if restaurant.business_status == "OPENING_SOON":
            score += 80.0
            confidence = 0.9
            evidence.append("Business status explicitly says 'OPENING_SOON'.")
        elif restaurant.business_status != "OPERATIONAL":
            score -= 10.0
            evidence.append(f"Business status is {restaurant.business_status}.")
            
        # 3. Discovery date (first seen)
        today = datetime.utcnow().date()
        if restaurant.first_seen:
            first_seen_date = restaurant.first_seen.date()
            if first_seen_date == today:
                score += 40.0
                confidence += 0.1
                evidence.append("Newly discovered today.")
            elif (today - first_seen_date).days < 30:
                score += 20.0
                evidence.append("Discovered within the last 30 days.")

        # Normalize score between 0 and 100
        score = max(0.0, min(100.0, score))
        confidence = min(1.0, confidence)
        
        # Status assignment
        status = "UNKNOWN"
        is_new = score >= 50.0
        
        if restaurant.first_seen and restaurant.first_seen.date() == today and restaurant.user_rating_count in (None, 0):
            status = "NEWLY_DISCOVERED"
        elif restaurant.business_status == "OPENING_SOON":
            status = "OPENING_SOON"
        elif score > 60:
            status = "LIKELY_NEW"
        elif score < 30 and restaurant.user_rating_count and restaurant.user_rating_count > 50:
            status = "ESTABLISHED"
            
        if not evidence:
            evidence.append("Insufficient data to determine newness.")
            
        return NewRestaurantResult(
            new_restaurant_score=score,
            is_new=is_new,
            confidence=confidence,
            reason=" | ".join(evidence),
            evidence=evidence,
            status=status
        )
