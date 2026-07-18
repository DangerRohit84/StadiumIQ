"""IoT sensor network subsystem for environmental monitoring.

Exposes the IoTSensorNetwork singleton that simulates and aggregates
readings from density, temperature, noise, air quality, and motion sensors.
"""
from core.iot.sensor_engine import sensor_network

__all__ = ["sensor_network"]
