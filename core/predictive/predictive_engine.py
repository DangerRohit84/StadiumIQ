"""Predictive Analytics Engine for crowd behavior and operations."""
import logging
import random
import time
from typing import Any

logger = logging.getLogger(__name__)


class PredictiveAnalytics:
    """ML-inspired predictive analytics for stadium operations."""

    EVENT_SCHEDULE = {
        "pre_match": {"hours_before": 2, "pattern": "gradual_increase"},
        "halftime": {"duration_min": 15, "pattern": "food_surge"},
        "post_match": {"pattern": "rapid_outflow"},
        "extra_time": {"pattern": "tension_buildup"},
    }

    def __init__(self) -> None:
        """Initialize predictive analytics with baseline patterns."""
        self._baseline_patterns = self._init_patterns()
        self._predictions = {}

    def _init_patterns(self) -> dict:
        """Initialize baseline crowd flow patterns per zone."""
        return {
            "A": {"base_flow": 150, "peak_multiplier": 2.5, "peak_time": "pre_kickoff"},
            "B": {"base_flow": 120, "peak_multiplier": 2.0, "peak_time": "pre_kickoff"},
            "C": {"base_flow": 180, "peak_multiplier": 3.0, "peak_time": "pre_kickoff"},
            "D": {"base_flow": 100, "peak_multiplier": 1.8, "peak_time": "pre_kickoff"},
        }

    def predict_demand(self, zone: str, minutes_ahead: int = 60) -> dict:
        """Predict demand for services in a zone."""
        logger.info("Predicting demand for zone=%s minutes_ahead=%d", zone, minutes_ahead)
        pattern = self._baseline_patterns.get(zone, self._baseline_patterns["A"])

        time_factor = self._time_based_factor(minutes_ahead)
        predicted_flow = pattern["base_flow"] * pattern["peak_multiplier"] * time_factor
        predicted_flow += random.gauss(0, pattern["base_flow"] * 0.1)

        return {
            "zone": zone,
            "predicted_flow_per_min": max(0, round(predicted_flow)),
            "confidence": round(0.75 + random.uniform(0, 0.2), 2),
            "peak_probability": round(random.uniform(0.3, 0.9), 2),
            "recommended_staff": max(3, round(predicted_flow / 50)),
            "food_demand": round(predicted_flow * 0.3),
            "restroom_demand": round(predicted_flow * 0.15),
        }

    def predict_resource_needs(self) -> dict:
        """Predict resource requirements for all zones."""
        needs = {}
        for zone in ["A", "B", "C", "D"]:
            prediction = self.predict_demand(zone)
            needs[zone] = {
                "staff_required": prediction["recommended_staff"],
                "food_supply": f"{prediction['food_demand']} servings",
                "restroom_capacity": f"{prediction['restroom_demand']} stalls needed",
                "security_presence": max(2, prediction["recommended_staff"] // 3),
                "medical_readiness": "standard" if prediction["confidence"] < 0.85 else "elevated",
            }
        return needs

    def predict_incident_risk(self, zone_data: dict) -> dict:
        """Predict likelihood of incidents based on current conditions."""
        logger.info("Predicting incident risk for %d zones", len(zone_data))
        risks = {}
        for zone_id, data in zone_data.items():
            density = data.get("percentage", 0) / 100
            trend = data.get("trend", "stable")

            crowd_risk = density * 0.6
            if trend == "increasing": crowd_risk += 0.15
            if density > 0.85: crowd_risk += 0.2

            total_risk = min(1.0, crowd_risk + random.uniform(0, 0.1))

            if total_risk > 0.8:
                level = "critical"
                action = "Deploy additional crowd management"
            elif total_risk > 0.6:
                level = "high"
                action = "Increase monitoring frequency"
            elif total_risk > 0.4:
                level = "moderate"
                action = "Standard monitoring"
            else:
                level = "low"
                action = "Normal operations"

            risks[zone_id] = {
                "risk_score": round(total_risk * 100, 1),
                "risk_level": level,
                "recommended_action": action,
                "factors": {
                    "crowd_density": round(crowd_risk * 100, 1),
                    "trend_impact": 15 if trend == "increasing" else 0,
                },
            }

        return risks

    def predict_wait_times(self) -> dict:
        """Predict wait times for various services."""
        return {
            "food_court": {
                "north": {"current": random.randint(5, 15), "predicted_15min": random.randint(8, 20)},
                "east": {"current": random.randint(8, 18), "predicted_15min": random.randint(10, 25)},
                "south": {"current": random.randint(3, 10), "predicted_15min": random.randint(5, 15)},
                "west": {"current": random.randint(6, 14), "predicted_15min": random.randint(8, 18)},
            },
            "restrooms": {
                "north": {"current": random.randint(1, 5), "predicted_15min": random.randint(2, 8)},
                "east": {"current": random.randint(2, 7), "predicted_15min": random.randint(3, 10)},
                "south": {"current": random.randint(1, 4), "predicted_15min": random.randint(2, 6)},
                "west": {"current": random.randint(1, 3), "predicted_15min": random.randint(1, 5)},
            },
            "entry_gates": {
                "E1": {"current": random.randint(2, 8), "predicted_15min": random.randint(3, 12)},
                "E2": {"current": random.randint(3, 10), "predicted_15min": random.randint(5, 15)},
                "E3": {"current": random.randint(2, 6), "predicted_15min": random.randint(3, 10)},
                "E4": {"current": random.randint(1, 3), "predicted_15min": random.randint(1, 5)},
            },
        }

    def generate_operational_insights(self) -> dict:
        """Generate comprehensive operational insights."""
        logger.info("Generating operational insights")
        return {
            "timestamp": time.time(),
            "crowd_prediction": self.predict_demand("A"),
            "incident_risk": self.predict_incident_risk({
                "A": {"percentage": 65, "trend": "stable"},
                "B": {"percentage": 45, "trend": "decreasing"},
                "C": {"percentage": 80, "trend": "increasing"},
                "D": {"percentage": 30, "trend": "stable"},
            }),
            "resource_needs": self.predict_resource_needs(),
            "wait_times": self.predict_wait_times(),
            "optimization_suggestions": [
                "Increase food supply to South Court — high demand expected",
                "Deploy 2 additional security staff to Zone C",
                "Open overflow restrooms in Zone A",
                "Promote Zone D parking to reduce North lot congestion",
            ],
        }

    def _time_based_factor(self, minutes_ahead: int) -> float:
        """Return a demand multiplier based on how far ahead we predict."""
        if minutes_ahead <= 15:
            return 1.0
        elif minutes_ahead <= 30:
            return 1.3
        elif minutes_ahead <= 60:
            return 1.5
        return 1.2


predictive_analytics = PredictiveAnalytics()
