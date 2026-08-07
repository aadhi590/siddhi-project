import json
import re
from typing import Dict, Any, List

from app.core.logging import get_logger
from app.database.models import Restaurant
from app.schemas.reports import MarketingReadinessResult
from app.utils.helpers import safe_float

logger = get_logger(__name__)

class MarketingReadinessService:
    """Service to calculate the marketing readiness score for a restaurant."""

    def __init__(self) -> None:
        pass

    def calculate_readiness(self, restaurant: Restaurant) -> MarketingReadinessResult:
        """Calculate the marketing readiness score based on observable signals."""
        score = 0.0
        evidence = {}
        reasons = []
        available_signals = 0
        total_signals = 12

        # 1. review_count_signal
        if restaurant.user_rating_count is not None:
            available_signals += 1
            count = restaurant.user_rating_count
            if count < 20:
                score += 15
                evidence['review_count'] = 15
                reasons.append("Very low review count indicates urgent need for marketing.")
            elif count <= 100:
                score += 10
                evidence['review_count'] = 10
                reasons.append("Low review count indicates room for growth.")
            elif count <= 500:
                score += 5
                evidence['review_count'] = 5
            else:
                evidence['review_count'] = 0

        # 2. rating_signal
        if restaurant.rating is not None:
            available_signals += 1
            rating = restaurant.rating
            if rating < 3.5:
                score -= 5
                evidence['rating'] = -5
            elif rating < 4.0:
                score += 5
                evidence['rating'] = 5
            elif rating < 4.5:
                score += 10
                evidence['rating'] = 10
                reasons.append("Good rating, excellent foundation for marketing.")
            else:
                score += 8
                evidence['rating'] = 8

        # 3. no_website
        available_signals += 1
        if not restaurant.website:
            score += 12
            evidence['no_website'] = 12
            reasons.append("No website found, major gap in digital presence.")
        else:
            evidence['no_website'] = 0

        # 4. no_instagram
        available_signals += 1
        has_insta = False
        if restaurant.website and 'instagram.com' in restaurant.website:
            has_insta = True
        if not has_insta:
            score += 10
            evidence['no_instagram'] = 10
            reasons.append("No Instagram presence detected.")
        else:
            evidence['no_instagram'] = 0

        # 5. low_online_presence
        available_signals += 1
        online_presence_score = getattr(restaurant, 'online_presence_score', 50)
        if online_presence_score < 30:
            score += 8
            evidence['low_online_presence'] = 8
            reasons.append("Overall online presence is very low.")
        else:
            evidence['low_online_presence'] = 0

        # 6. opening_status
        if restaurant.business_status:
            available_signals += 1
            status = restaurant.business_status.upper()
            if status == 'OPENING_SOON':
                score += 15
                evidence['opening_status'] = 15
                reasons.append("Opening soon, prime time for pre-launch marketing.")
            elif status == 'NEWLY_OPENED':
                score += 12
                evidence['opening_status'] = 12
                reasons.append("Newly opened, needs awareness campaigns.")
            else:
                evidence['opening_status'] = 0

        # 7. premium_area
        available_signals += 1
        premium_zones = ['nungambakkam', 'adyar', 'ecr', 't nagar', 'omr']
        addr = (restaurant.formatted_address or "").lower()
        if any(zone in addr for zone in premium_zones):
            score += 8
            evidence['premium_area'] = 8
            reasons.append("Located in a premium area, high potential for targeted marketing.")
        else:
            evidence['premium_area'] = 0

        # 8. high_competition
        available_signals += 1
        comp_count = getattr(restaurant, 'competitor_count', 0)
        if comp_count > 8:
            score += 10
            evidence['high_competition'] = 10
            reasons.append("High competition area, requires strong differentiation.")
        else:
            evidence['high_competition'] = 0

        # 9. vision_quality
        available_signals += 1
        if restaurant.vision_labels:
            labels_str = str(restaurant.vision_labels).lower()
            if 'premium' in labels_str or 'luxury' in labels_str or 'high quality' in labels_str:
                score += 8
                evidence['vision_quality'] = 8
                reasons.append("Visuals suggest premium positioning.")
            else:
                evidence['vision_quality'] = 0
        else:
            evidence['vision_quality'] = 0

        # 10. price_level
        if restaurant.price_level is not None:
            available_signals += 1
            if restaurant.price_level >= 3:
                score += 8
                evidence['price_level'] = 8
                reasons.append("Premium pricing suggests higher marketing budget capability.")
            else:
                evidence['price_level'] = 0

        # 11. branding_score
        available_signals += 1
        branding_score_val = getattr(restaurant, 'branding_score', 50)
        if branding_score_val < 40:
            score += 10
            evidence['branding_score'] = 10
            reasons.append("Low branding score indicates need for branding refresh.")
        else:
            evidence['branding_score'] = 0

        # 12. new_restaurant
        available_signals += 1
        is_new = getattr(restaurant, 'is_new', False)
        if is_new:
            score += 10
            evidence['new_restaurant'] = 10
            reasons.append("New restaurant requires aggressive initial marketing.")
        else:
            evidence['new_restaurant'] = 0

        confidence = (available_signals / total_signals) * 100
        score = min(score, 100.0)

        # Truncate reasons to top 5
        reasons = reasons[:5]

        return MarketingReadinessResult(
            score=score,
            confidence=confidence,
            evidence=evidence,
            reasons=reasons
        )
