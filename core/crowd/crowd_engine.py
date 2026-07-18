"""Advanced crowd management engine with flow analysis and prediction."""
import logging
import random
import time
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)

LOW_THRESHOLD = 40
MODERATE_THRESHOLD = 65
HIGH_THRESHOLD = 80
CRITICAL_THRESHOLD = 95
HISTORY_MAX_LEN = 100


class CrowdManager:
    """Real-time crowd intelligence engine."""

    ZONES = {
        "A": {"name": "North Stand", "capacity": 20000, "sections": ["A1", "A2", "A3", "A4", "A5"]},
        "B": {"name": "East Stand", "capacity": 20000, "sections": ["B1", "B2", "B3", "B4", "B5"]},
        "C": {"name": "South Stand", "capacity": 20000, "sections": ["C1", "C2", "C3", "C4", "C5"]},
        "D": {"name": "West Stand", "capacity": 22500, "sections": ["D1", "D2", "D3", "D4", "D5"]},
    }

    def __init__(self) -> None:
        self._occupancy: dict[str, int] = {z: random.randint(3000, 15000) for z in self.ZONES}
        self._flow_rates: dict[str, dict[str, int]] = {z: {"inflow": 0, "outflow": 0} for z in self.ZONES}
        self._history: dict[str, deque] = {z: deque(maxlen=HISTORY_MAX_LEN) for z in self.ZONES}
        self._update_cycle: int = 0

    def update(self) -> dict:
        """Simulate crowd movement with realistic patterns."""
        self._update_cycle += 1
        updates = {}

        for zone_id, zone in self.ZONES.items():
            current = self._occupancy[zone_id]
            capacity = zone["capacity"]

            inflow = random.randint(10, 300)
            outflow = random.randint(10, 250)
            noise = random.randint(-50, 50)

            new_occ = current + inflow - outflow + noise
            new_occ = max(0, min(capacity, new_occ))

            self._occupancy[zone_id] = new_occ
            self._flow_rates[zone_id] = {"inflow": inflow, "outflow": outflow}

            self._history[zone_id].append({
                "time": time.time(),
                "occupancy": new_occ,
                "inflow": inflow,
                "outflow": outflow,
            })

            updates[zone_id] = self.get_zone_status(zone_id)

        return updates

    def get_zone_status(self, zone_id: str) -> dict:
        """Get detailed status for a zone."""
        zone = self.ZONES.get(zone_id)
        if not zone:
            return {}

        occupancy = self._occupancy[zone_id]
        capacity = zone["capacity"]
        pct = (occupancy / capacity * 100) if capacity > 0 else 0

        if pct < LOW_THRESHOLD:
            level = "low"
            risk = "minimal"
        elif pct < MODERATE_THRESHOLD:
            level = "moderate"
            risk = "low"
        elif pct < HIGH_THRESHOLD:
            level = "high"
            risk = "moderate"
        elif pct < CRITICAL_THRESHOLD:
            level = "critical"
            risk = "high"
        else:
            level = "overflow"
            risk = "severe"

        flow = self._flow_rates[zone_id]
        trend = "increasing" if flow["inflow"] > flow["outflow"] else "decreasing"
        if abs(flow["inflow"] - flow["outflow"]) < 20:
            trend = "stable"

        hist = self._history[zone_id]
        hist_list = list(hist)
        peak_30m = max((h["occupancy"] for h in hist_list[-30:]), default=occupancy) if hist_list else occupancy
        avg_30m = (sum(h["occupancy"] for h in hist_list[-30:]) / min(30, len(hist_list))) if hist_list else occupancy

        return {
            "zone_id": zone_id,
            "name": zone["name"],
            "occupancy": occupancy,
            "capacity": capacity,
            "percentage": round(pct, 1),
            "level": level,
            "risk": risk,
            "trend": trend,
            "inflow": flow["inflow"],
            "outflow": flow["outflow"],
            "peak_30min": peak_30m,
            "average_30min": round(avg_30m),
            "sections": zone["sections"],
        }

    def get_all_zones(self) -> dict:
        """Get status of all zones."""
        return {z: self.get_zone_status(z) for z in self.ZONES}

    def get_stadium_overview(self) -> dict:
        """Get overall stadium metrics."""
        total_occ = sum(self._occupancy.values())
        total_cap = sum(z["capacity"] for z in self.ZONES.values())
        total_inflow = sum(f["inflow"] for f in self._flow_rates.values())
        total_outflow = sum(f["outflow"] for f in self._flow_rates.values())

        zones = self.get_all_zones()
        critical = [z for z, s in zones.items() if s["level"] in ("critical", "overflow")]
        recommendations = self._generate_recommendations(zones)

        return {
            "total_occupancy": total_occ,
            "total_capacity": total_cap,
            "overall_density": round(total_occ / total_cap * 100, 1),
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "net_flow": total_inflow - total_outflow,
            "zones": zones,
            "critical_zones": critical,
            "recommendations": recommendations,
            "timestamp": time.time(),
        }

    def get_heatmap_data(self) -> list[dict]:
        """Generate heatmap data for visualization."""
        heatmap: list[dict] = []
        for zone_id, zone in self.ZONES.items():
            occ = self._occupancy[zone_id]

            for i, section in enumerate(zone["sections"]):
                section_occ = occ / len(zone["sections"])
                section_pct = section_occ / (zone["capacity"] / len(zone["sections"]))
                variance = random.uniform(0.8, 1.2)
                final_pct = min(1.0, section_pct * variance)

                heatmap.append({
                    "zone": zone_id,
                    "section": section,
                    "density": round(final_pct * 100, 1),
                    "x": self._section_x(zone_id, i),
                    "y": self._section_y(zone_id, i),
                })

        return heatmap

    def predict_flow(self, minutes_ahead: int = 30) -> dict:
        """Predict crowd flow for the next N minutes."""
        if minutes_ahead < 1:
            logger.warning("Invalid minutes_ahead=%d, clamping to 1", minutes_ahead)
            minutes_ahead = 1
        elif minutes_ahead > 1440:
            logger.warning("minutes_ahead=%d exceeds max, clamping to 1440", minutes_ahead)
            minutes_ahead = 1440

        predictions: dict[str, dict] = {}
        for zone_id in self.ZONES:
            hist = list(self._history[zone_id])[-10:]
            if len(hist) < 2:
                predictions[zone_id] = {"predicted_occupancy": self._occupancy[zone_id], "confidence": 0.5}
                continue

            recent_trend = hist[-1]["occupancy"] - hist[0]["occupancy"]
            per_step = recent_trend / len(hist)
            predicted = self._occupancy[zone_id] + per_step * minutes_ahead
            predicted = max(0, min(self.ZONES[zone_id]["capacity"], predicted))

            confidence = min(0.95, 0.6 + len(hist) * 0.03)

            predictions[zone_id] = {
                "predicted_occupancy": round(predicted),
                "predicted_percentage": round(predicted / self.ZONES[zone_id]["capacity"] * 100, 1),
                "confidence": round(confidence, 2),
                "trend": "increasing" if per_step > 5 else "decreasing" if per_step < -5 else "stable",
            }

        return predictions

    def _generate_recommendations(self, zones: dict) -> list[dict]:
        recs: list[dict] = []
        for zid, status in zones.items():
            if status["level"] in ("critical", "overflow"):
                recs.append({
                    "type": "redirect",
                    "priority": "high",
                    "zone": zid,
                    "message": f"Zone {zid} ({status['name']}) at {status['percentage']}% — redirect incoming fans",
                })
            elif status["level"] == "high":
                recs.append({
                    "type": "monitor",
                    "priority": "medium",
                    "zone": zid,
                    "message": f"Zone {zid} approaching capacity — prepare overflow sections",
                })

        low_zones = [z for z, s in zones.items() if s["level"] == "low"]
        if low_zones:
            recs.append({
                "type": "promote",
                "priority": "low",
                "zones": low_zones,
                "message": f"Zones {', '.join(low_zones)} have availability — promote to incoming fans",
            })

        return recs

    def _section_x(self, zone: str, idx: int) -> float:
        positions = {"A": [30, 40, 50, 60, 70], "B": [80, 80, 80, 80, 80],
                     "C": [30, 40, 50, 60, 70], "D": [20, 20, 20, 20, 20]}
        return positions.get(zone, [50] * 5)[idx]

    def _section_y(self, zone: str, idx: int) -> float:
        positions = {"A": [20, 20, 20, 20, 20], "B": [30, 40, 50, 60, 70],
                     "C": [80, 80, 80, 80, 80], "D": [30, 40, 50, 60, 70]}
        return positions.get(zone, [50] * 5)[idx]


crowd_manager = CrowdManager()
