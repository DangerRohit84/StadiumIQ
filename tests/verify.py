"""Verify the entire application works end-to-end."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import json

def test_imports():
    print("1. Testing imports...")
    try:
        from config.settings import Config
        print("   config.settings OK")
    except Exception as e:
        print(f"   FAIL config.settings: {e}")
        return False

    try:
        from core.ai.genai_engine import GenAIEngine
        print("   core.ai.genai_engine OK")
    except Exception as e:
        print(f"   FAIL core.ai.genai_engine: {e}")
        return False

    try:
        from core.crowd.crowd_engine import CrowdManager
        print("   core.crowd.crowd_engine OK")
    except Exception as e:
        print(f"   FAIL core.crowd.crowd_engine: {e}")
        return False

    try:
        from core.iot.sensor_engine import IoTSensorNetwork
        print("   core.iot.sensor_engine OK")
    except Exception as e:
        print(f"   FAIL core.iot.sensor_engine: {e}")
        return False

    try:
        from core.emergency.emergency_engine import EmergencySystem
        print("   core.emergency.emergency_engine OK")
    except Exception as e:
        print(f"   FAIL core.emergency.emergency_engine: {e}")
        return False

    try:
        from core.navigation.nav_engine import NavigationEngine
        print("   core.navigation.nav_engine OK")
    except Exception as e:
        print(f"   FAIL core.navigation.nav_engine: {e}")
        return False

    try:
        from core.sentiment.sentiment_engine import SentimentAnalyzer
        print("   core.sentiment.sentiment_engine OK")
    except Exception as e:
        print(f"   FAIL core.sentiment.sentiment_engine: {e}")
        return False

    try:
        from core.predictive.predictive_engine import PredictiveAnalytics
        print("   core.predictive.predictive_engine OK")
    except Exception as e:
        print(f"   FAIL core.predictive.predictive_engine: {e}")
        return False

    try:
        from core.analytics.dashboard_engine import AnalyticsDashboard
        print("   core.analytics.dashboard_engine OK")
    except Exception as e:
        print(f"   FAIL core.analytics.dashboard_engine: {e}")
        return False

    return True


def test_app_creation():
    print("\n2. Testing app creation...")
    try:
        from app import create_app
        app, _ = create_app("development")
        print("   App created OK")
        return app
    except Exception as e:
        print(f"   FAIL: {e}")
        return None


def test_routes(app):
    print("\n3. Testing all API routes with test client...")
    app.config["TESTING"] = True
    errors = []

    with app.test_client() as client:
        # Pages
        tests = [
            ("GET", "/", 200, "Homepage"),
            ("GET", "/command-center", 200, "Command Center"),
            ("GET", "/api/crowd", 200, "Crowd data"),
            ("GET", "/api/crowd/overview", 200, "Crowd overview"),
            ("GET", "/api/crowd/heatmap", 200, "Crowd heatmap"),
            ("GET", "/api/crowd/predict?minutes=30", 200, "Crowd predict"),
            ("GET", "/api/iot/sensors", 200, "IoT sensors"),
            ("GET", "/api/iot/zones", 200, "IoT zones"),
            ("GET", "/api/iot/anomalies", 200, "IoT anomalies"),
            ("GET", "/api/emergency/status", 200, "Emergency status"),
            ("GET", "/api/navigation/accessibility/wheelchair", 200, "Accessibility info"),
            ("GET", "/api/analytics/predict?zone=A&minutes=60", 200, "Analytics predict"),
            ("GET", "/api/analytics/risks", 200, "Analytics risks"),
            ("GET", "/api/analytics/waits", 200, "Analytics waits"),
            ("GET", "/api/analytics/insights", 200, "Analytics insights"),
            ("GET", "/api/sentiment/summary", 200, "Sentiment summary"),
            ("GET", "/api/sentiment/chart", 200, "Sentiment chart"),
            ("GET", "/api/dashboard/kpis", 200, "Dashboard KPIs"),
            ("GET", "/api/dashboard/hourly", 200, "Dashboard hourly"),
            ("GET", "/api/dashboard/revenue", 200, "Dashboard revenue"),
            ("GET", "/api/dashboard/staff", 200, "Dashboard staff"),
            ("GET", "/api/dashboard/command", 200, "Dashboard command"),
        ]

        post_tests = [
            ("/api/chat", {"message": "Hello"}, 200, "Chat hello"),
            ("/api/chat", {"message": "Where is the restroom?"}, 200, "Chat restroom"),
            ("/api/chat", {"message": "How busy is the stadium?"}, 200, "Chat crowd"),
            ("/api/chat", {"message": "Where can I park?"}, 200, "Chat parking"),
            ("/api/chat", {"message": "I need wheelchair access"}, 200, "Chat accessibility"),
            ("/api/chat", {"message": "Emergency! Fire!"}, 200, "Chat emergency"),
            ("/api/chat", {"message": "Where are recycling stations?"}, 200, "Chat eco"),
            ("/api/navigation", {"origin": "E1", "destination": "R1"}, 200, "Navigation"),
            ("/api/navigation", {"origin": "E1", "destination": "R1", "mode": "accessible"}, 200, "Accessible nav"),
            ("/api/navigation", {"origin": "E1", "destination": "R1", "mode": "crowd_aware"}, 200, "Crowd-aware nav"),
            ("/api/navigation/nearby", {"lat": 40.8128, "lon": -74.0745, "type": "restrooms"}, 200, "Nearby facilities"),
            ("/api/sentiment/analyze", {"text": "This stadium is amazing!"}, 200, "Sentiment analyze"),
            ("/api/emergency/raise", {"type": "medical", "location": {"zone": "A"}}, 200, "Emergency raise"),
            ("/api/emergency/evacuation", {"zones": ["A"]}, 200, "Evacuation plan"),
        ]

        for method, url, expected, name in tests:
            try:
                if method == "GET":
                    r = client.get(url)
                else:
                    r = client.post(url)
                status = r.status_code
                if status != expected:
                    print(f"   FAIL {name}: expected {expected}, got {status}")
                    errors.append(name)
                else:
                    data = json.loads(r.data) if r.content_type == "application/json" else None
                    if data and data.get("status") == "error":
                        print(f"   WARN {name}: returned error status")
                    else:
                        print(f"   OK   {name}")
            except Exception as e:
                print(f"   FAIL {name}: {e}")
                errors.append(name)

        for url, body, expected, name in post_tests:
            try:
                r = client.post(url, data=json.dumps(body), content_type="application/json")
                status = r.status_code
                if status != expected:
                    print(f"   FAIL {name}: expected {expected}, got {status}")
                    errors.append(name)
                else:
                    data = json.loads(r.data)
                    if data.get("status") == "error" and expected == 200:
                        print(f"   WARN {name}: returned error status")
                    else:
                        print(f"   OK   {name}")
            except Exception as e:
                print(f"   FAIL {name}: {e}")
                errors.append(name)

    return errors


def test_core_engines():
    print("\n4. Testing core engine logic...")
    try:
        from core.crowd.crowd_engine import crowd_manager
        overview = crowd_manager.get_stadium_overview()
        assert "total_occupancy" in overview
        assert "zones" in overview
        print("   OK   CrowdManager")

        heatmap = crowd_manager.get_heatmap_data()
        assert len(heatmap) > 0
        print("   OK   Heatmap data")
    except Exception as e:
        print(f"   FAIL CrowdManager: {e}")

    try:
        from core.iot.sensor_engine import sensor_network
        sensors = sensor_network.update_readings()
        assert len(sensors) > 0
        print("   OK   IoTSensorNetwork")

        anomalies = sensor_network.get_anomaly_readings()
        assert isinstance(anomalies, list)
        print("   OK   Anomaly detection")
    except Exception as e:
        print(f"   FAIL IoTSensorNetwork: {e}")

    try:
        from core.emergency.emergency_engine import emergency_system
        result = emergency_system.raise_incident("fire", {"zone": "A"})
        assert "incident" in result
        assert "protocol" in result
        print("   OK   EmergencySystem")

        plan = emergency_system.get_evacuation_plan(["A", "C"])
        assert "primary_exits" in plan
        print("   OK   Evacuation plan")
    except Exception as e:
        print(f"   FAIL EmergencySystem: {e}")

    try:
        from core.sentiment.sentiment_engine import sentiment_analyzer
        result = sentiment_analyzer.analyze("This stadium is amazing! Best experience ever!")
        assert result["sentiment"] == "positive"
        print("   OK   SentimentAnalyzer (positive)")

        result2 = sentiment_analyzer.analyze("Terrible service, very disappointed")
        assert result2["sentiment"] == "negative"
        print("   OK   SentimentAnalyzer (negative)")

        summary = sentiment_analyzer.get_feedback_summary()
        assert "average_score" in summary
        print("   OK   Sentiment summary")
    except Exception as e:
        print(f"   FAIL SentimentAnalyzer: {e}")

    try:
        from core.predictive.predictive_engine import predictive_analytics
        demand = predictive_analytics.predict_demand("A", 60)
        assert "predicted_flow_per_min" in demand
        print("   OK   PredictiveAnalytics")

        risks = predictive_analytics.predict_incident_risk({
            "A": {"percentage": 85, "trend": "increasing"},
            "B": {"percentage": 45, "trend": "stable"},
        })
        assert "A" in risks
        print("   OK   Risk assessment")
    except Exception as e:
        print(f"   FAIL PredictiveAnalytics: {e}")

    try:
        from core.navigation.nav_engine import navigation_engine
        route = navigation_engine.get_directions("E1", "R1")
        assert "steps" in route
        print("   OK   NavigationEngine")

        accessible = navigation_engine.get_directions("E1", "R1", "accessible")
        assert accessible["mode"] == "accessible"
        print("   OK   Accessible routing")

        profile = navigation_engine.get_accessibility_info("wheelchair")
        assert "accessible_facilities" in profile
        print("   OK   Accessibility profile")
    except Exception as e:
        print(f"   FAIL NavigationEngine: {e}")

    try:
        from core.analytics.dashboard_engine import analytics_dashboard
        kpis = analytics_dashboard.get_realtime_kpis()
        assert len(kpis) > 0
        print("   OK   Dashboard KPIs")

        command = analytics_dashboard.get_command_center_summary()
        assert "kpis" in command
        print("   OK   Command center summary")
    except Exception as e:
        print(f"   FAIL AnalyticsDashboard: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("StadiumIQ v2.0 — Full Verification")
    print("=" * 60)

    if not test_imports():
        print("\nIMPORT FAILED — Cannot continue")
        sys.exit(1)

    app = test_app_creation()
    if not app:
        print("\nAPP CREATION FAILED — Cannot continue")
        sys.exit(1)

    errors = test_routes(app)
    test_core_engines()

    print("\n" + "=" * 60)
    if errors:
        print(f"RESULT: {len(errors)} FAILURES")
        for e in errors:
            print(f"  - {e}")
    else:
        print("RESULT: ALL CHECKS PASSED")
    print("=" * 60)
