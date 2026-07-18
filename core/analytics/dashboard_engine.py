"""Analytics Dashboard Engine for operational intelligence."""
import time
import random
from typing import Any


class AnalyticsDashboard:
    """Provides real-time analytics and KPI tracking for stadium operations."""

    def __init__(self):
        self._kpi_history = []
        self._alerts = []

    def get_realtime_kpis(self) -> dict:
        """Get current key performance indicators."""
        kpis = {
            "fan_satisfaction": {
                "value": round(random.uniform(4.0, 4.8), 1),
                "target": 4.5,
                "unit": "/5",
                "trend": "stable",
            },
            "avg_entry_time": {
                "value": random.randint(3, 8),
                "target": 5,
                "unit": "min",
                "trend": "improving",
            },
            "food_wait_time": {
                "value": random.randint(5, 15),
                "target": 8,
                "unit": "min",
                "trend": "stable",
            },
            "safety_score": {
                "value": random.randint(85, 100),
                "target": 95,
                "unit": "%",
                "trend": "improving",
            },
            "eco_points_issued": {
                "value": random.randint(5000, 15000),
                "target": 20000,
                "unit": "pts",
                "trend": "increasing",
            },
            "active_incidents": {
                "value": random.randint(0, 3),
                "target": 0,
                "unit": "",
                "trend": "stable",
            },
        }

        self._kpi_history.append({"time": time.time(), "kpis": kpis})
        if len(self._kpi_history) > 100:
            self._kpi_history = self._kpi_history[-100:]

        return kpis

    def get_hourly_analytics(self) -> dict:
        """Generate hourly analytics data."""
        hours = []
        for i in range(12):
            hour = 14 + i
            if hour >= 24: hour -= 24
            hours.append({
                "hour": f"{hour:02d}:00",
                "attendance": random.randint(30000, 82500),
                "incidents": random.randint(0, 5),
                "avg_satisfaction": round(random.uniform(3.8, 4.8), 1),
                "food_revenue": random.randint(50000, 200000),
                "merch_revenue": random.randint(30000, 150000),
            })
        return {"hourly_data": hours}

    def get_zone_performance(self) -> dict:
        """Get performance metrics by zone."""
        zones = {}
        for zone_id in ["A", "B", "C", "D"]:
            zones[zone_id] = {
                "occupancy_rate": round(random.uniform(30, 95), 1),
                "fan_satisfaction": round(random.uniform(3.5, 5.0), 1),
                "incident_count": random.randint(0, 3),
                "avg_wait_time": random.randint(2, 15),
                "facility_utilization": round(random.uniform(40, 90), 1),
                "staff_efficiency": round(random.uniform(70, 98), 1),
            }
        return zones

    def get_revenue_analytics(self) -> dict:
        """Get revenue analytics."""
        return {
            "total_revenue": random.randint(500000, 1500000),
            "breakdown": {
                "food_beverage": random.randint(200000, 600000),
                "merchandise": random.randint(100000, 400000),
                "parking": random.randint(80000, 250000),
                "vip_packages": random.randint(100000, 300000),
            },
            "eco_credits_issued": random.randint(5000, 15000),
            "sustainability_savings": random.randint(10000, 50000),
        }

    def get_staff_deployment(self) -> dict:
        """Get current staff deployment status."""
        departments = {
            "security": {"deployed": random.randint(40, 60), "total": 60, "locations": ["All gates", "Concourse", "VIP area"]},
            "medical": {"deployed": random.randint(5, 8), "total": 8, "locations": ["Station North", "Station South", "Roaming"]},
            "crowd_mgmt": {"deployed": random.randint(15, 25), "total": 30, "locations": ["Zone A", "Zone B", "Zone C", "Zone D"]},
            "cleaning": {"deployed": random.randint(20, 35), "total": 40, "locations": ["Restrooms", "Food courts", "Concourse"]},
            "guest_services": {"deployed": random.randint(10, 20), "total": 25, "locations": ["Info desks", "Accessibility desk", "VIP lounge"]},
        }

        return {
            "departments": departments,
            "total_deployed": sum(d["deployed"] for d in departments.values()),
            "total_staff": sum(d["total"] for d in departments.values()),
            "utilization_rate": round(
                sum(d["deployed"] for d in departments.values()) /
                sum(d["total"] for d in departments.values()) * 100, 1
            ),
        }

    def get_command_center_summary(self) -> dict:
        """Get high-level summary for command center."""
        return {
            "timestamp": time.time(),
            "overall_status": "operational",
            "kpis": self.get_realtime_kpis(),
            "zone_performance": self.get_zone_performance(),
            "staff": self.get_staff_deployment(),
            "alerts": self._alerts[-10:],
            "recent_events": [
                {"time": time.time() - 120, "type": "info", "message": "Zone C approaching 80% capacity"},
                {"time": time.time() - 300, "type": "success", "message": "Halftime rush managed successfully"},
                {"time": time.time() - 600, "type": "warning", "message": "Food Court East wait time exceeds 15 min"},
            ],
        }


analytics_dashboard = AnalyticsDashboard()
