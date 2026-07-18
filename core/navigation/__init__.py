"""Navigation subsystem with pathfinding and accessibility routing.

Exposes the NavigationEngine singleton that provides crowd-aware
routes, nearby facility lookups, and accessibility profiles.
"""
from core.navigation.nav_engine import navigation_engine

__all__ = ["navigation_engine"]
