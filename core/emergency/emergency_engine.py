"""Emergency Response System with real-time incident management."""
import time
from typing import Any


class EmergencySystem:
    """Manages emergency incidents, evacuation protocols, and safety."""

    INCIDENT_TYPES = {
        "fire": {"severity": "critical", "response_time": 2, "evacuation": True},
        "medical": {"severity": "high", "response_time": 3, "evacuation": False},
        "crowd_surge": {"severity": "high", "response_time": 1, "evacuation": True},
        "structural": {"severity": "critical", "response_time": 1, "evacuation": True},
        "security_threat": {"severity": "critical", "response_time": 1, "evacuation": True},
        "power_outage": {"severity": "medium", "response_time": 5, "evacuation": False},
        "severe_weather": {"severity": "high", "response_time": 0, "evacuation": True},
    }

    def __init__(self):
        self.active_incidents = []
        self.incident_history = []
        self.alert_level = "green"
        self.evacuation_zones = set()

    def raise_incident(self, incident_type: str, location: dict, details: str = "") -> dict:
        """Raise a new emergency incident."""
        config = self.INCIDENT_TYPES.get(incident_type, {
            "severity": "medium", "response_time": 5, "evacuation": False
        })

        incident = {
            "id": f"INC-{len(self.active_incidents) + len(self.incident_history) + 1:04d}",
            "type": incident_type,
            "severity": config["severity"],
            "location": location,
            "details": details,
            "timestamp": time.time(),
            "status": "active",
            "response_time_min": config["response_time"],
            "evacuation_required": config["evacuation"],
            "assigned_team": None,
            "resolution_notes": None,
        }

        self.active_incidents.append(incident)
        self._update_alert_level()

        if config["evacuation"]:
            zone = location.get("zone", "unknown")
            self.evacuation_zones.add(zone)

        return {
            "incident": incident,
            "protocol": self._get_protocol(incident_type, location),
            "alert_level": self.alert_level,
        }

    def resolve_incident(self, incident_id: str, notes: str = "") -> dict:
        """Resolve an active incident."""
        for inc in self.active_incidents:
            if inc["id"] == incident_id:
                inc["status"] = "resolved"
                inc["resolved_at"] = time.time()
                inc["resolution_notes"] = notes
                self.active_incidents.remove(inc)
                self.incident_history.append(inc)
                self._update_alert_level()
                return {"resolved": True, "incident": inc}

        return {"resolved": False, "error": "Incident not found"}

    def get_active_alerts(self) -> list:
        """Get all active incidents sorted by severity."""
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_incidents = sorted(
            self.active_incidents,
            key=lambda x: severity_order.get(x["severity"], 4)
        )
        return sorted_incidents

    def get_safety_status(self) -> dict:
        """Get overall stadium safety status."""
        return {
            "alert_level": self.alert_level,
            "active_incidents": len(self.active_incidents),
            "critical_count": sum(1 for i in self.active_incidents if i["severity"] == "critical"),
            "evacuation_zones": list(self.evacuation_zones),
            "safety_score": self._calculate_safety_score(),
            "recommendations": self._safety_recommendations(),
        }

    def get_evacuation_plan(self, affected_zones: list) -> dict:
        """Generate evacuation plan for affected zones."""
        return {
            "affected_zones": affected_zones,
            "primary_exits": self._get_exits_for_zones(affected_zones),
            "secondary_exits": self._get_secondary_exits(affected_zones),
            "assembly_points": [
                "North Parking Lot", "South Parking Lot", "East Open Field",
            ],
            "medical_stations": ["Station North (Gate E1)", "Station South (Gate E3)"],
            "estimated_evacuation_time": f"{len(affected_zones) * 5} minutes",
            "pa_announcement": (
                "Attention please. Due to a safety incident, we are initiating "
                "a controlled evacuation. Please remain calm and follow the "
                "illuminated exit signs. Staff members are positioned to assist you."
            ),
        }

    def _update_alert_level(self):
        if any(i["severity"] == "critical" for i in self.active_incidents):
            self.alert_level = "red"
        elif any(i["severity"] == "high" for i in self.active_incidents):
            self.alert_level = "orange"
        elif len(self.active_incidents) > 3:
            self.alert_level = "yellow"
        else:
            self.alert_level = "green"

    def _calculate_safety_score(self) -> int:
        score = 100
        for inc in self.active_incidents:
            if inc["severity"] == "critical": score -= 30
            elif inc["severity"] == "high": score -= 20
            elif inc["severity"] == "medium": score -= 10
            else: score -= 5
        return max(0, score)

    def _safety_recommendations(self) -> list:
        recs = []
        if self.alert_level == "red":
            recs.append("IMMEDIATE: Evacuate affected zones")
            recs.append("Contact emergency services (911)")
        elif self.alert_level == "orange":
            recs.append("Increase security patrols in affected areas")
            recs.append("Prepare evacuation routes")
        elif self.alert_level == "yellow":
            recs.append("Monitor situation closely")
            recs.append("Alert response teams")
        else:
            recs.append("All systems normal")
        return recs

    def _get_protocol(self, incident_type: str, location: dict) -> dict:
        protocols = {
            "fire": {
                "steps": [
                    "Activate fire alarm", "Notify fire department",
                    "Begin zone evacuation", "Deploy suppression teams",
                ],
                "communication": "PA + push notification + digital signage",
            },
            "medical": {
                "steps": [
                    "Dispatch medical team", "Clear access route",
                    "Notify medical station", "Prepare ambulance",
                ],
                "communication": "Staff radio + internal alert",
            },
            "crowd_surge": {
                "steps": [
                    "Activate density alerts", "Deploy crowd staff",
                    "Open overflow gates", "PA crowd control message",
                ],
                "communication": "PA + mobile app alert + signage",
            },
        }
        return protocols.get(incident_type, {
            "steps": ["Assess situation", "Notify security", "Establish perimeter"],
            "communication": "Staff radio",
        })

    def _get_exits_for_zones(self, zones: list) -> list:
        exit_map = {
            "A": ["E1 - North Main", "E2 - East Gate"],
            "B": ["E2 - East Gate", "E4 - VIP"],
            "C": ["E3 - South Gate", "E1 - North Main"],
            "D": ["E4 - VIP", "E3 - South Gate"],
        }
        exits = []
        for z in zones:
            exits.extend(exit_map.get(z, ["E1 - Main Gate"]))
        return list(set(exits))

    def _get_secondary_exits(self, zones: list) -> list:
        return ["Service Tunnel A", "Service Tunnel B", "Emergency Stairs North", "Emergency Stairs South"]


emergency_system = EmergencySystem()
