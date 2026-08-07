from datetime import datetime, timezone
from app.database.models import Restaurant
from app.schemas.intelligence import OpportunityScoreResult

class OpportunityScoreService:
    def __init__(self) -> None:
        self.premium_zones = ["Nungambakkam", "Adyar", "ECR", "T Nagar"]

    def calculate_opportunity_score(self, restaurant: Restaurant) -> OpportunityScoreResult:
        """Calculates the overall opportunity score for a given restaurant."""
        score = 0
        reasons = []

        if not restaurant.website:
            score += 15
            reasons.append("No website")

        contact_instagram = getattr(restaurant, "contact_instagram", None)
        if not contact_instagram:
            score += 10
            reasons.append("No Instagram linked")

        if restaurant.user_rating_count is not None and restaurant.user_rating_count < 50:
            score += 15
            reasons.append("Low review count")

        vision_labels = getattr(restaurant, "vision_labels", []) or []
        if isinstance(vision_labels, list) and any("premium" in str(label).lower() or "luxury" in str(label).lower() for label in vision_labels):
            score += 10
            reasons.append("Premium interior quality")

        scan_zone = getattr(restaurant, "scan_zone", "")
        if scan_zone in self.premium_zones:
            score += 10
            reasons.append(f"Located in premium area ({scan_zone})")

        opening_status = getattr(restaurant, "opening_status", None)
        if opening_status in ["OPENING_SOON", "NEWLY_OPENED"]:
            score += 15
            reasons.append(f"Opening status: {opening_status}")

        competitor_count = getattr(restaurant, "competitor_count", 10)
        if competitor_count < 5:
            score += 10
            reasons.append("Few local competitors")

        if hasattr(restaurant, "first_seen") and restaurant.first_seen:
            now = datetime.now(timezone.utc)
            days = (now - restaurant.first_seen.replace(tzinfo=timezone.utc)).days
            if days <= 7:
                score += 10
                reasons.append("Recently discovered")

        premium_score = getattr(restaurant, "premium_score", 0) or 0
        score += 5 * (premium_score / 100.0)

        score = min(score, 100)
        reason_str = ", ".join(reasons)

        return OpportunityScoreResult(
            score=score,
            reason=reason_str
        )
