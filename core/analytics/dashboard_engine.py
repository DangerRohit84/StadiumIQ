"""Analytics Dashboard Engine for operational intelligence."""
import hashlib
import math
import time
from typing import Any

from core.crowd.crowd_engine import crowd_manager
from core.emergency.emergency_engine import emergency_system


STADIUM_CAPACITY = sum(z["capacity"] for z in crowd_manager.ZONES.values())

BASE_STAFFING = {
    "security":     {"total": 60, "locations": ["All gates", "Concourse", "VIP area"]},
    "medical":      {"total": 8,  "locations": ["Station North", "Station South", "Roaming"]},
    "crowd_mgmt":   {"total": 30, "locations": ["Zone A", "Zone B", "Zone C", "Zone D"]},
    "cleaning":     {"total": 40, "locations": ["Restrooms", "Food courts", "Concourse"]},
    "guest_services": {"total": 25, "locations": ["Info desks", "Accessibility desk", "VIP lounge"]},
}


def _time_bucket(interval: int = 30) -> int:
    """Return an integer that changes every `interval` seconds."""
    return int(time.time() // interval)


def _seeded_random(seed: int, index: int = 0) -> float:
    """Return a deterministic float in [0, 1) for a given seed + index."""
    h = hashlib.sha256(f"{seed}:{index}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _seeded_int(seed: int, index: int, lo: int, hi: int) -> int:
    """Return a deterministic integer in [lo, hi]."""
    return lo + int(_seeded_random(seed, index) * (hi - lo + 1))


def _seeded_float(seed: int, index: int, lo: float, hi: float) -> float:
    """Return a deterministic float in [lo, hi)."""
    return lo + _seeded_random(seed, index) * (hi - lo)


def _match_day_pattern(hour: int) -> float:
    """Return a multiplier (0.0-1.0) for a given hour simulating a match day.

    Typical match day: gates open ~2h before kickoff at 15:00,
    peak during match 15:00-17:00, post-match spike, taper off.
    """
    pattern = {
        0: 0.05, 1: 0.03, 2: 0.02, 3: 0.02, 4: 0.02, 5: 0.03,
        6: 0.05, 7: 0.08, 8: 0.12, 9: 0.18, 10: 0.25, 11: 0.35,
        12: 0.50, 13: 0.65, 14: 0.85, 15: 1.00, 16: 0.95, 17: 0.80,
        18: 0.55, 19: 0.40, 20: 0.30, 21: 0.22, 22: 0.15, 23: 0.08,
    }
    return pattern.get(hour, 0.05)


def _get_current_hour() -> int:
    """Return the current hour of the day (0-23)."""
    return time.localtime().tm_hour


def _get_minute_of_day() -> int:
    """Return the current minute of the day (0-1439)."""
    lt = time.localtime()
    return lt.tm_hour * 60 + lt.tm_min


class AnalyticsDashboard:
    """Provides real-time analytics and KPI tracking for stadium operations.

    All values are deterministic: the same call within the same time bucket
    returns identical data.  Values change every 30 seconds (or per the
    specified bucket interval) to keep the dashboard coherent across polls.
    """

    def __init__(self):
        self._kpi_history: list[dict] = []
        self._alerts: list[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_realtime_kpis(self) -> dict:
        """Get current key performance indicators.

        Uses real occupancy from crowd_manager, real safety score from
        emergency_system, and time-bucketed deterministic values for
        sentiment-derived KPIs.
        """
        bucket = _time_bucket(30)
        overview = crowd_manager.get_stadium_overview()
        safety = emergency_system.get_safety_status()

        total_occ = overview["total_occupancy"]
        density = overview["overall_density"]

        # Fan satisfaction: 3.5-4.9 range, shifts slowly with density
        base_satisfaction = 4.2
        density_effect = (density - 50) * -0.008          # higher density → slightly lower
        bucket_bump = _seeded_float(bucket, 10, -0.15, 0.15)
        fan_satisfaction = round(max(3.0, min(5.0, base_satisfaction + density_effect + bucket_bump)), 1)

        # Entry time: scales with occupancy
        base_entry = 4
        occ_factor = int(total_occ / 20000)
        entry_time = max(2, min(12, base_entry + occ_factor + _seeded_int(bucket, 20, -1, 1)))

        # Food wait: busier → longer waits
        base_wait = 6
        wait_time = max(3, min(18, base_wait + occ_factor + _seeded_int(bucket, 30, -2, 3)))

        # Safety score: directly from emergency_system
        safety_score = safety["safety_score"]

        # Eco points: deterministic per bucket, slowly accumulating
        eco_points = 5000 + (bucket % 100) * 50 + _seeded_int(bucket, 40, 0, 200)

        # Active incidents: from emergency_system
        active_incidents = safety["active_incidents"]

        # Trend classification
        def _trend(metric: str, value: float) -> str:
            prev_bucket = bucket - 1
            prev_val = _seeded_float(prev_bucket, hash(metric) % 1000, 0, 1)
            cur_val = _seeded_float(bucket, hash(metric) % 1000, 0, 1)
            diff = cur_val - prev_val
            if diff > 0.05:
                return "improving" if metric in ("fan_satisfaction", "safety_score") else "increasing"
            elif diff < -0.05:
                return "declining"
            return "stable"

        kpis = {
            "fan_satisfaction": {
                "value": fan_satisfaction,
                "target": 4.5,
                "unit": "/5",
                "trend": _trend("fan_satisfaction", fan_satisfaction),
            },
            "avg_entry_time": {
                "value": entry_time,
                "target": 5,
                "unit": "min",
                "trend": "improving" if entry_time <= 5 else "declining",
            },
            "food_wait_time": {
                "value": wait_time,
                "target": 8,
                "unit": "min",
                "trend": "stable",
            },
            "safety_score": {
                "value": safety_score,
                "target": 95,
                "unit": "%",
                "trend": "improving" if safety_score >= 95 else "stable",
            },
            "eco_points_issued": {
                "value": eco_points,
                "target": 20000,
                "unit": "pts",
                "trend": "increasing",
            },
            "active_incidents": {
                "value": active_incidents,
                "target": 0,
                "unit": "",
                "trend": "stable" if active_incidents == 0 else "declining",
            },
        }

        self._kpi_history.append({"time": time.time(), "kpis": kpis})
        if len(self._kpi_history) > 100:
            self._kpi_history = self._kpi_history[-100:]

        return kpis

    def get_hourly_analytics(self) -> dict:
        """Generate deterministic 24-hour analytics (match-day pattern).

        Returns the next 12 hours starting from the current hour, with
        attendance, incidents, satisfaction, and revenue shaped by the
        match-day curve.
        """
        bucket = _time_bucket(3600)  # one bucket per hour
        current_hour = _get_current_hour()
        hours = []

        for i in range(12):
            hour = (current_hour + i) % 24
            pattern = _match_day_pattern(hour)

            seed = bucket * 100 + hour
            attendance = int(pattern * STADIUM_CAPACITY * _seeded_float(seed, 1, 0.85, 1.0))
            attendance = max(500, min(STADIUM_CAPACITY, attendance))

            max_incidents = max(1, int(pattern * 8))
            incidents = _seeded_int(seed, 2, 0, max_incidents)

            avg_sat = round(3.5 + pattern * 1.3 + _seeded_float(seed, 3, -0.2, 0.2), 1)
            avg_sat = max(3.0, min(5.0, avg_sat))

            food_rev = int(pattern * 180000 * _seeded_float(seed, 4, 0.8, 1.1))
            merch_rev = int(pattern * 120000 * _seeded_float(seed, 5, 0.7, 1.2))

            hours.append({
                "hour": f"{hour:02d}:00",
                "attendance": attendance,
                "incidents": incidents,
                "avg_satisfaction": avg_sat,
                "food_revenue": food_rev,
                "merch_revenue": merch_rev,
            })

        return {"hourly_data": hours}

    def get_zone_performance(self) -> dict:
        """Get performance metrics per zone using real occupancy data."""
        overview = crowd_manager.get_stadium_overview()
        zones_data = overview.get("zones", {})
        bucket = _time_bucket(30)
        zones = {}

        for zone_id in ["A", "B", "C", "D"]:
            zd = zones_data.get(zone_id, {})
            occ_pct = zd.get("percentage", 50)

            seed = bucket * 10 + ord(zone_id)
            zones[zone_id] = {
                "occupancy_rate": round(occ_pct, 1),
                "fan_satisfaction": round(max(3.0, min(5.0, 4.5 - (occ_pct - 50) * 0.01 + _seeded_float(seed, 1, -0.2, 0.2))), 1),
                "incident_count": _seeded_int(seed, 2, 0, max(0, int((occ_pct - 70) / 10))),
                "avg_wait_time": max(1, min(20, 3 + int(occ_pct / 20) + _seeded_int(seed, 3, -1, 2))),
                "facility_utilization": round(max(30, min(95, occ_pct * 0.9 + _seeded_float(seed, 4, -5, 5))), 1),
                "staff_efficiency": round(max(65, min(99, 85 - (occ_pct - 50) * 0.15 + _seeded_float(seed, 5, -3, 3))), 1),
            }
        return zones

    def get_revenue_analytics(self) -> dict:
        """Get revenue analytics with fixed baseline + time variation."""
        bucket = _time_bucket(60)  # changes every minute
        current_hour = _get_current_hour()
        day_factor = _match_day_pattern(current_hour)

        # Base daily targets
        base_food = 400000
        base_merch = 250000
        base_parking = 150000
        base_vip = 200000

        # Accumulated proportion based on hour
        hour_acc = sum(_match_day_pattern(h) for h in range(current_hour + 1)) / sum(_match_day_pattern(h) for h in range(24))
        hour_acc = max(0.0, min(1.0, hour_acc))

        variation = _seeded_float(bucket, 1, 0.92, 1.08)

        food = int(base_food * hour_acc * variation)
        merch = int(base_merch * hour_acc * variation)
        parking = int(base_parking * hour_acc * _seeded_float(bucket, 2, 0.90, 1.10))
        vip = int(base_vip * hour_acc * _seeded_float(bucket, 3, 0.88, 1.12))
        total = food + merch + parking + vip

        eco_credits = _seeded_int(bucket, 4, 5000, 15000)
        sustainability = _seeded_int(bucket, 5, 10000, 50000)

        return {
            "total_revenue": total,
            "breakdown": {
                "food_beverage": food,
                "merchandise": merch,
                "parking": parking,
                "vip_packages": vip,
            },
            "eco_credits_issued": eco_credits,
            "sustainability_savings": sustainability,
        }

    def get_staff_deployment(self) -> dict:
        """Get staff deployment scaled to current occupancy."""
        overview = crowd_manager.get_stadium_overview()
        density = overview["overall_density"]
        bucket = _time_bucket(60)

        # Scale factor: 40% at low density, up to 100% at 80%+ capacity
        scale = max(0.40, min(1.0, 0.30 + density / 100))

        departments = {}
        for dept, info in BASE_STAFFING.items():
            total = info["total"]
            # Each department has a slightly different scale
            dept_seed = bucket * 10 + hash(dept) % 100
            dept_scale = scale + _seeded_float(dept_seed, 1, -0.05, 0.05)
            dept_scale = max(0.30, min(1.0, dept_scale))
            deployed = max(1, min(total, int(total * dept_scale)))

            departments[dept] = {
                "deployed": deployed,
                "total": total,
                "locations": info["locations"],
            }

        total_deployed = sum(d["deployed"] for d in departments.values())
        total_staff = sum(d["total"] for d in departments.values())

        return {
            "departments": departments,
            "total_deployed": total_deployed,
            "total_staff": total_staff,
            "utilization_rate": round(total_deployed / total_staff * 100, 1) if total_staff else 0,
        }

    def get_command_center_summary(self) -> dict:
        """Get high-level summary combining data from all engines."""
        overview = crowd_manager.get_stadium_overview()
        safety = emergency_system.get_safety_status()
        zone_perf = self.get_zone_performance()
        staff = self.get_staff_deployment()
        kpis = self.get_realtime_kpis()

        # Build deterministic recent events from crowd recommendations
        bucket = _time_bucket(60)
        events = []
        for i, rec in enumerate(overview.get("recommendations", [])[:3]):
            events.append({
                "time": time.time() - (i + 1) * 120,
                "type": rec.get("priority", "info"),
                "message": rec.get("message", ""),
            })

        # If no crowd events, add defaults
        if not events:
            events = [
                {"time": time.time() - 120, "type": "info", "message": "All zones within normal capacity"},
                {"time": time.time() - 300, "type": "success", "message": "Systems operating normally"},
            ]

        # Determine overall status
        if safety["alert_level"] == "red":
            status = "emergency"
        elif safety["alert_level"] == "orange":
            status = "alert"
        elif overview["overall_density"] > 80:
            status = "high_traffic"
        else:
            status = "operational"

        return {
            "timestamp": time.time(),
            "overall_status": status,
            "kpis": kpis,
            "zone_performance": zone_perf,
            "staff": staff,
            "alerts": self._alerts[-10:],
            "recent_events": events,
        }


analytics_dashboard = AnalyticsDashboard()
