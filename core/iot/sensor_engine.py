"""IoT Sensor Simulation Engine for smart stadium."""
import logging
import random
import time
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)


class IoTSensorNetwork:
    """Simulates a network of IoT sensors throughout the stadium."""

    SENSOR_TYPES = [
        "crowd_density", "temperature", "humidity", "noise",
        "air_quality", "co2", "light", "motion", "flow_rate",
    ]

    def __init__(self) -> None:
        """Initialize the IoT sensor network."""
        self.sensors: dict[str, dict] = self._init_sensors()
        self._last_update: float = time.time()

    def _init_sensors(self) -> dict[str, dict]:
        """Initialize all sensors across zones."""
        sensors: dict[str, dict] = {}
        zones = ["A", "B", "C", "D"]
        sensor_id = 1

        for zone in zones:
            for stype in self.SENSOR_TYPES:
                sensors[f"SZ{zone}-{stype[:3].upper()}-{sensor_id:03d}"] = {
                    "sensor_id": f"SZ{zone}-{stype[:3].upper()}-{sensor_id:03d}",
                    "zone": zone,
                    "type": stype,
                    "value": self._get_initial_value(stype),
                    "unit": self._get_unit(stype),
                    "status": "active",
                    "last_reading": time.time(),
                    "battery": random.randint(70, 100),
                }
                sensor_id += 1

        return sensors

    def _get_initial_value(self, stype: str) -> float:
        defaults = {
            "crowd_density": random.uniform(20, 70),
            "temperature": random.uniform(20, 28),
            "humidity": random.uniform(40, 70),
            "noise": random.uniform(60, 90),
            "air_quality": random.uniform(30, 80),
            "co2": random.uniform(400, 800),
            "light": random.uniform(300, 800),
            "motion": random.uniform(0, 100),
            "flow_rate": random.uniform(10, 200),
        }
        return round(defaults.get(stype, 50), 2)

    def _get_unit(self, stype: str) -> str:
        units = {
            "crowd_density": "%",
            "temperature": "°C",
            "humidity": "%",
            "noise": "dB",
            "air_quality": "AQI",
            "co2": "ppm",
            "light": "lux",
            "motion": "count/min",
            "flow_rate": "person/min",
        }
        return units.get(stype, "")

    def update_readings(self) -> dict[str, dict]:
        """Simulate sensor updates with realistic fluctuations."""
        self._last_update = time.time()
        updated = {}

        for sid, sensor in self.sensors.items():
            drift = random.gauss(0, 2)
            new_value = sensor["value"] + drift
            new_value = max(0, new_value)

            if sensor["type"] == "temperature":
                new_value = max(15, min(40, new_value))
            elif sensor["type"] == "humidity":
                new_value = max(20, min(95, new_value))
            elif sensor["type"] == "noise":
                new_value = max(30, min(120, new_value))
            elif sensor["type"] == "crowd_density":
                new_value = max(0, min(100, new_value))
            elif sensor["type"] == "co2":
                new_value = max(300, min(2000, new_value))

            sensor["value"] = round(new_value, 2)
            sensor["last_reading"] = time.time()
            sensor["battery"] = max(0, sensor["battery"] - random.uniform(0, 0.01))
            updated[sid] = sensor

        return updated

    def get_zone_summary(self, zone: str) -> dict[str, Any]:
        """Get aggregated sensor data for a zone."""
        zone_sensors = {k: v for k, v in self.sensors.items() if v["zone"] == zone}
        if not zone_sensors:
            return {}

        summary = {"zone": zone, "sensors": {}}
        for stype in self.SENSOR_TYPES:
            readings = [s["value"] for s in zone_sensors.values() if s["type"] == stype]
            if readings:
                summary["sensors"][stype] = {
                    "avg": round(sum(readings) / len(readings), 2),
                    "min": round(min(readings), 2),
                    "max": round(max(readings), 2),
                    "count": len(readings),
                }

        return summary

    def get_all_zone_summaries(self) -> dict:
        """Get summaries for all zones."""
        return {zone: self.get_zone_summary(zone) for zone in ["A", "B", "C", "D"]}

    def get_anomaly_readings(self, threshold: float = 2.0) -> list[dict]:
        """Identify sensors with anomalous readings.

        Pre-groups sensors by (zone, type) to avoid O(n²) lookups.
        """
        groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for sensor in self.sensors.values():
            groups[(sensor["zone"], sensor["type"])].append(sensor)

        anomalies: list[dict] = []
        for group_sensors in groups.values():
            if len(group_sensors) < 2:
                continue
            values = [s["value"] for s in group_sensors]
            mean = sum(values) / len(values)
            std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

            if std > 0:
                for s in group_sensors:
                    deviation = abs(s["value"] - mean) / std
                    if deviation > threshold:
                        anomalies.append({
                            "sensor_id": s["sensor_id"],
                            "type": s["type"],
                            "zone": s["zone"],
                            "value": s["value"],
                            "expected": round(mean, 2),
                            "deviation": round(deviation, 2),
                        })

        return anomalies


sensor_network = IoTSensorNetwork()
