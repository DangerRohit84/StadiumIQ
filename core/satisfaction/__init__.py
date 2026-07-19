"""Fan Satisfaction Scoring System — real-time satisfaction tracking."""
import logging
import time
from typing import Any

from core.types import SatisfactionScore

logger = logging.getLogger(__name__)

MAX_SCORES = 1000
MAX_OVERALL_HISTORY = 1000
MAX_NPS_RESPONSES = 1000


class SatisfactionTracker:
    """Tracks and analyzes fan satisfaction across all touchpoints."""

    TOUCHPOINTS = [
        "entry_experience", "seating_comfort", "food_quality", "food_wait_time",
        "restroom_cleanliness", "staff_friendliness", "safety_feeling",
        "view_quality", "match_excitement", "exit_experience",
        "accessibility", "wifi_quality", "value_for_money",
    ]

    def __init__(self) -> None:
        """Initialize the satisfaction tracker."""
        self.scores: dict[str, list[dict]] = {tp: [] for tp in self.TOUCHPOINTS}
        self.overall_history: list[dict] = []
        self._nps_responses: list[dict] = []

    def record_score(self, touchpoint: str, score: int, fan_id: str | None = None) -> SatisfactionScore | dict[str, Any]:
        """Record a satisfaction score for a touchpoint (1-10)."""
        if touchpoint not in self.TOUCHPOINTS:
            return {"error": f"Unknown touchpoint: {touchpoint}"}

        score = max(1, min(10, score))
        self.scores[touchpoint].append({
            "score": score,
            "time": time.time(),
            "fan_id": fan_id,
        })
        if len(self.scores[touchpoint]) > MAX_SCORES:
            self.scores[touchpoint] = self.scores[touchpoint][-MAX_SCORES:]

        overall = self.get_overall_score()
        self.overall_history.append({"time": time.time(), "score": overall})
        if len(self.overall_history) > MAX_OVERALL_HISTORY:
            self.overall_history = self.overall_history[-MAX_OVERALL_HISTORY:]

        return {"touchpoint": touchpoint, "score": score, "overall": overall}

    def record_nps(self, score: int, fan_id: str | None = None) -> dict:
        """Record Net Promoter Score (0-10)."""
        score = max(0, min(10, score))
        self._nps_responses.append({"score": score, "time": time.time(), "fan_id": fan_id})
        if len(self._nps_responses) > MAX_NPS_RESPONSES:
            self._nps_responses = self._nps_responses[-MAX_NPS_RESPONSES:]
        return self.get_nps()

    def get_overall_score(self) -> float:
        """Calculate overall satisfaction score."""
        all_scores: list[int] = []
        for tp_scores in self.scores.values():
            all_scores.extend([s["score"] for s in tp_scores[-20:]])
        if not all_scores:
            return 0.0
        return round(sum(all_scores) / len(all_scores), 1)

    def get_touchpoint_scores(self) -> dict:
        """Get average score for each touchpoint."""
        result = {}
        for tp, scores in self.scores.items():
            recent = [s["score"] for s in scores[-10:]]
            if recent:
                avg = round(sum(recent) / len(recent), 1)
                trend = "improving" if len(recent) >= 2 and recent[-1] > recent[0] else "declining" if len(recent) >= 2 and recent[-1] < recent[0] else "stable"
            else:
                avg = 0
                trend = "no_data"
            result[tp] = {"average": avg, "count": len(scores), "trend": trend}
        return result

    def get_nps(self) -> dict:
        """Calculate Net Promoter Score."""
        if not self._nps_responses:
            return {"nps": 0, "promoters": 0, "passives": 0, "detractors": 0, "responses": 0}

        scores = [r["score"] for r in self._nps_responses[-100:]]
        promoters = sum(1 for s in scores if s >= 9)
        passives = sum(1 for s in scores if 7 <= s <= 8)
        detractors = sum(1 for s in scores if s <= 6)
        total = len(scores)

        nps = round(((promoters - detractors) / total) * 100) if total > 0 else 0

        return {
            "nps": nps,
            "promoters": promoters,
            "passives": passives,
            "detractors": detractors,
            "responses": total,
            "rating": "excellent" if nps > 50 else "good" if nps > 0 else "needs_improvement",
        }

    def get_satisfaction_trend(self, last_n: int = 50) -> list:
        """Get satisfaction trend over time."""
        return self.overall_history[-last_n:]

    def get_weakest_areas(self, count: int = 3) -> list:
        """Identify the weakest satisfaction areas."""
        tp_scores = self.get_touchpoint_scores()
        sorted_tps = sorted(
            [(tp, data) for tp, data in tp_scores.items() if data["count"] > 0],
            key=lambda x: x[1]["average"]
        )
        return [{"touchpoint": tp, **data} for tp, data in sorted_tps[:count]]

    def get_dashboard_data(self) -> dict:
        """Get comprehensive satisfaction dashboard data."""
        return {
            "overall_score": self.get_overall_score(),
            "nps": self.get_nps(),
            "touchpoints": self.get_touchpoint_scores(),
            "weakest_areas": self.get_weakest_areas(),
            "total_responses": sum(len(s) for s in self.scores.values()),
            "trend": self.get_satisfaction_trend(),
        }


satisfaction_tracker = SatisfactionTracker()
