"""Crowd management subsystem with flow analysis and density prediction.

Exposes the CrowdManager singleton that tracks zone occupancy,
calculates congestion levels, and forecasts crowd movement.
"""
from core.crowd.crowd_engine import crowd_manager

__all__ = ["crowd_manager"]
