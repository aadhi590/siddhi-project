from typing import Dict, Any, List

from app.core.logging import get_logger
from app.database.models import Restaurant
from app.schemas.reports import OpportunityIndexResult

logger = get_logger(__name__)

class OpportunityIndexService:
    """Service to calculate the overall master opportunity index."""

    def __init__(self) -> None:
        pass

    def calculate_index(self, restaurant: Restaurant) -> OpportunityIndexResult:
        """Calculate the master opportunity index blending all phase scores."""
        score = 0.0
        available_scores = 0
        total_scores = 10
        evidence = {}
        top_contributors = []
        reasons = []

        def process_score(val, weight, name, inverted=False, is_available=True):
            nonlocal score, available_scores
            if is_available and val is not None:
                available_scores += 1
                effective_val = (100 - val) if inverted else val
                contrib = (effective_val / 100.0) * weight
                score += contrib
                evidence[name] = val
                return contrib
            else:
                contrib = (50.0 / 100.0) * weight
                score += contrib
                evidence[name] = "Default 50 used (unavailable)"
                return contrib

        # 1. marketing_readiness_score (20%)
        mkt_score = getattr(restaurant, 'marketing_readiness_score', None)
        c1 = process_score(mkt_score, 20, 'marketing_readiness', is_available=mkt_score is not None)
        if mkt_score and mkt_score > 70:
            top_contributors.append("High marketing readiness")
            reasons.append("Restaurant shows strong signs of needing marketing intervention.")

        # 2. new_restaurant_score (15%)
        is_new = getattr(restaurant, 'is_new', False)
        new_score = 100 if is_new else 0
        c2 = process_score(new_score, 15, 'new_restaurant', is_available=True)
        if is_new:
            top_contributors.append("New Restaurant Bonus")
            reasons.append("New establishments have higher urgency for digital services.")

        # 3. competition opportunity (10%)
        comp_count = getattr(restaurant, 'competitor_count', None)
        if comp_count is not None:
            comp_score = max(0, 100 - (comp_count * 10))
        else:
            comp_score = None
        c3 = process_score(comp_score, 10, 'competition', is_available=comp_count is not None)

        # 4. branding_score (10%)
        brand_score = getattr(restaurant, 'branding_score', None)
        c4 = process_score(brand_score, 10, 'branding_score', inverted=True, is_available=brand_score is not None)
        if brand_score is not None and brand_score < 40:
            top_contributors.append("Low Branding Score")
            reasons.append("Poor existing branding presents a clear service opportunity.")

        # 5. premium_score (10%)
        prem_score = getattr(restaurant, 'premium_score', None)
        c5 = process_score(prem_score, 10, 'premium_score', is_available=prem_score is not None)

        # 6. digital_presence gap (10%)
        dig_score = getattr(restaurant, 'online_presence_score', None)
        c6 = process_score(dig_score, 10, 'digital_presence', inverted=True, is_available=dig_score is not None)

        # 7. vision quality signals (5%)
        vis_score = 100 if restaurant.vision_labels else 0
        c7 = process_score(vis_score, 5, 'vision_quality', is_available=bool(restaurant.vision_labels))

        # 8. collaboration_score (10%)
        collab_score = getattr(restaurant, 'collaboration_score', None)
        c8 = process_score(collab_score, 10, 'collaboration_score', is_available=collab_score is not None)

        # 9. opening_status bonus (5%)
        status = restaurant.business_status
        open_score = 0
        if status in ['OPENING_SOON', 'NEWLY_OPENED']:
            open_score = 100
            top_contributors.append("Opening Soon / Newly Opened")
        c9 = process_score(open_score, 5, 'opening_status', is_available=bool(status))

        # 10. opportunity_score (Phase 2) (5%)
        opp_score_p2 = getattr(restaurant, 'opportunity_score', None)
        c10 = process_score(opp_score_p2, 5, 'opportunity_score_p2', is_available=opp_score_p2 is not None)

        confidence = (available_scores / total_scores) * 100 if total_scores > 0 else 0

        # Cap score
        score = min(max(score, 0.0), 100.0)

        if not reasons:
            reasons.append("Standard evaluation complete based on available signals.")

        return OpportunityIndexResult(
            score=score,
            confidence=confidence,
            evidence=evidence,
            top_contributors=top_contributors[:5],
            reasons=reasons
        )
