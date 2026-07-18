"""Analytics dashboard subsystem for operational KPI tracking.

Exposes the AnalyticsDashboard singleton that aggregates real-time
KPIs, hourly trends, revenue metrics, and staff deployment data.
"""
from core.analytics.dashboard_engine import analytics_dashboard

__all__ = ["analytics_dashboard"]
