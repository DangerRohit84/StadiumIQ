"""Predictive analytics subsystem for demand forecasting and risk assessment.

Exposes the PredictiveAnalytics singleton that forecasts service demand,
wait times, and incident risk across stadium zones.
"""
from core.predictive.predictive_engine import predictive_analytics

__all__ = ["predictive_analytics"]
