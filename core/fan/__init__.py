"""Smart Fan Journey Tracker — tracks and personalizes the entire fan experience."""
import time
from typing import Any


class FanJourney:
    """Tracks a fan's complete stadium experience from arrival to departure."""

    JOURNEY_STAGES = [
        {"id": "pre_arrival", "name": "Pre-Arrival", "icon": "fa-home", "tips": [
            "Check match schedule and weather forecast",
            "Pre-book parking via StadiumIQ app",
            "Download offline stadium map",
        ]},
        {"id": "arrival", "name": "Arrival", "icon": "fa-car", "tips": [
            "Use E1 or E3 for shortest entry queues",
            "Show digital ticket at gate scan point",
            "Pick up accessibility wristband if needed",
        ]},
        {"id": "entry", "name": "Entry & Seating", "icon": "fa-door-open", "tips": [
            "Follow section signage to your seat",
            "Locate nearest restroom and food court",
            "Enable StadiumIQ notifications for updates",
        ]},
        {"id": "pre_match", "name": "Pre-Match", "icon": "fa-clock", "tips": [
            "Arrive 30 min before kickoff for best atmosphere",
            "Grab food early to avoid halftime rush",
            "Explore merchandise stores",
        ]},
        {"id": "match_live", "name": "Live Match", "icon": "fa-futbol", "tips": [
            "Enjoy the game! Check live stats in StadiumIQ",
            "Use quick-order for halftime food",
            "Report any issues via the app",
        ]},
        {"id": "halftime", "name": "Halftime", "icon": "fa-coffee", "tips": [
            "Best time to visit restrooms — lower queues",
            "Food courts get busy — order ahead",
            "Check live match analytics",
        ]},
        {"id": "post_match", "name": "Post-Match", "icon": "fa-flag-checkered", "tips": [
            "Wait 10 min for crowds to clear",
            "Use South exits for faster departure",
            "Rate your experience for eco-points",
        ]},
        {"id": "departure", "name": "Departure", "icon": "fa-sign-out-alt", "tips": [
            "Follow staff directions to parking/transit",
            "Check rideshare surge pricing",
            "Leave feedback to help improve",
        ]},
    ]

    def __init__(self):
        self.active_fans = {}
        self.journey_analytics = {
            "total_fans_tracked": 0,
            "avg_satisfaction": 4.3,
            "stage_completion": {s["id"]: 0 for s in self.JOURNEY_STAGES},
        }

    def start_journey(self, fan_id: str, preferences: dict | None = None) -> dict:
        """Start tracking a fan's journey."""
        prefs = preferences or {}
        self.active_fans[fan_id] = {
            "fan_id": fan_id,
            "current_stage": "pre_arrival",
            "stage_history": [{"stage": "pre_arrival", "time": time.time()}],
            "preferences": {
                "accessibility": prefs.get("accessibility", []),
                "language": prefs.get("language", "en"),
                "dietary": prefs.get("dietary", []),
                "interests": prefs.get("interests", ["football", "food"]),
            },
            "satisfaction_scores": {},
            "completed_actions": [],
            "started_at": time.time(),
        }
        self.journey_analytics["total_fans_tracked"] += 1

        return self.get_journey_status(fan_id)

    def advance_stage(self, fan_id: str, stage_id: str | None = None) -> dict:
        """Advance fan to next stage or specific stage."""
        fan = self.active_fans.get(fan_id)
        if not fan:
            return {"error": "Fan not found"}

        if stage_id:
            fan["current_stage"] = stage_id
        else:
            current_idx = next(
                (i for i, s in enumerate(self.JOURNEY_STAGES) if s["id"] == fan["current_stage"]),
                0
            )
            if current_idx < len(self.JOURNEY_STAGES) - 1:
                fan["current_stage"] = self.JOURNEY_STAGES[current_idx + 1]["id"]

        fan["stage_history"].append({"stage": fan["current_stage"], "time": time.time()})
        self.journey_analytics["stage_completion"][fan["current_stage"]] += 1

        return self.get_journey_status(fan_id)

    def get_journey_status(self, fan_id: str) -> dict:
        """Get current journey status with personalized recommendations."""
        fan = self.active_fans.get(fan_id)
        if not fan:
            return {"error": "Fan not found"}

        current = next(
            (s for s in self.JOURNEY_STAGES if s["id"] == fan["current_stage"]),
            self.JOURNEY_STAGES[0]
        )

        stage_idx = next(
            (i for i, s in enumerate(self.JOURNEY_STAGES) if s["id"] == fan["current_stage"]),
            0
        )

        next_stage = self.JOURNEY_STAGES[stage_idx + 1] if stage_idx < len(self.JOURNEY_STAGES) - 1 else None
        prev_stage = self.JOURNEY_STAGES[stage_idx - 1] if stage_idx > 0 else None

        personalized_tips = self._personalize_tips(current["tips"], fan["preferences"])

        elapsed = time.time() - fan["started_at"]
        avg_stage_time = elapsed / max(1, len(fan["stage_history"]))

        return {
            "fan_id": fan_id,
            "current_stage": current,
            "progress_percent": round((stage_idx / (len(self.JOURNEY_STAGES) - 1)) * 100),
            "next_stage": next_stage,
            "prev_stage": prev_stage,
            "personalized_tips": personalized_tips,
            "elapsed_time_min": round(elapsed / 60, 1),
            "estimated_remaining_min": round(avg_stage_time * (len(self.JOURNEY_STAGES) - stage_idx - 1) / 60, 1),
            "completed_actions": fan["completed_actions"],
            "satisfaction": fan["satisfaction_scores"],
        }

    def complete_action(self, fan_id: str, action: str, rating: int | None = None) -> dict:
        """Record a completed action and optional satisfaction rating."""
        fan = self.active_fans.get(fan_id)
        if not fan:
            return {"error": "Fan not found"}

        fan["completed_actions"].append({
            "action": action,
            "time": time.time(),
            "stage": fan["current_stage"],
        })

        if rating is not None:
            fan["satisfaction_scores"][fan["current_stage"]] = max(1, min(10, rating))

        return {"status": "recorded", "action": action}

    def get_personalized_recommendations(self, fan_id: str) -> list:
        """Get AI-powered personalized recommendations based on journey position."""
        fan = self.active_fans.get(fan_id)
        if not fan:
            return []

        stage = fan["current_stage"]
        prefs = fan["preferences"]
        recs = []

        if stage in ("pre_arrival", "arrival"):
            recs.append({
                "type": "navigation",
                "priority": "high",
                "message": "Use Gate E1 (North) for fastest entry — current wait: ~3 min",
                "action": {"type": "navigate", "destination": "E1"},
            })
            if prefs.get("accessibility"):
                recs.append({
                    "type": "accessibility",
                    "priority": "high",
                    "message": "Accessible entrance available at all gates. Staff can assist.",
                    "action": {"type": "accessibility_info"},
                })

        elif stage in ("entry", "pre_match"):
            recs.append({
                "type": "food",
                "priority": "medium",
                "message": "Food Court South has shortest wait (5 min) and vegan/halal options",
                "action": {"type": "navigate", "destination": "F3"},
            })
            recs.append({
                "type": "facility",
                "priority": "low",
                "message": "Nearest restroom: 2 min walk. VIP restroom available with no queue.",
                "action": {"type": "navigate", "destination": "R1"},
            })

        elif stage == "match_live":
            recs.append({
                "type": "engagement",
                "priority": "low",
                "message": "Check live match stats and crowd energy in the analytics tab",
                "action": {"type": "view_analytics"},
            })

        elif stage == "halftime":
            recs.append({
                "type": "food",
                "priority": "high",
                "message": "Halftime rush starting — pre-order via StadiumIQ app now",
                "action": {"type": "pre_order"},
            })
            recs.append({
                "type": "facility",
                "priority": "medium",
                "message": "Restroom queues building — West restroom still has shortest wait",
                "action": {"type": "navigate", "destination": "R4"},
            })

        elif stage in ("post_match", "departure"):
            recs.append({
                "type": "transport",
                "priority": "high",
                "message": "Crowds clearing — use South exits for faster departure",
                "action": {"type": "navigate", "destination": "E3"},
            })
            recs.append({
                "type": "sustainability",
                "priority": "low",
                "message": "Recycle your cup at Eco Station South for +75 eco points",
                "action": {"type": "navigate", "destination": "RC3"},
            })

        if prefs.get("accessibility"):
            recs.append({
                "type": "accessibility",
                "priority": "medium",
                "message": "Tactile paving available on all main routes. Audio guide active.",
                "action": {"type": "accessibility"},
            })

        return recs

    def get_analytics(self) -> dict:
        """Get journey analytics for organizers."""
        return self.journey_analytics

    def _personalize_tips(self, tips: list, prefs: dict) -> list:
        personalized = list(tips)
        if prefs.get("accessibility"):
            personalized.insert(0, "Accessibility: All routes have ramp/elevator access")
        if prefs.get("dietary"):
            dietary = ", ".join(prefs["dietary"])
            personalized.append(f"Food: {dietary} options available at Food Court South")
        return personalized


fan_journey = FanJourney()
