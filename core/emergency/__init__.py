"""Emergency response subsystem for incident management and evacuation.

Exposes the EmergencySystem singleton that handles incident lifecycle,
alert levels, and zone-based evacuation planning.
"""
from core.emergency.emergency_engine import emergency_system

__all__ = ["emergency_system"]
