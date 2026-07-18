"""Comprehensive test suite for StadiumIQ."""
import json
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app("development")
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ═══ Page Tests ═══════════════════════════════════════════════
class TestPages:
    def test_index(self, client):
        assert client.get("/").status_code == 200

    def test_index_contains_title(self, client):
        assert b"StadiumIQ" in client.get("/").data

    def test_command_center(self, client):
        assert client.get("/command-center").status_code == 200


# ═══ AI Chat Tests ════════════════════════════════════════════
class TestAIChat:
    def test_chat_requires_message(self, client):
        r = client.post("/api/chat", data=json.dumps({}), content_type="application/json")
        assert r.status_code == 400

    def test_chat_hello(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "Hello"}), content_type="application/json")
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"
        assert len(d["data"]["response"]) > 10
        assert "source" in d["data"]

    def test_chat_restroom(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "Where is the nearest restroom?"}), content_type="application/json")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_food(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "What food options are available?"}), content_type="application/json")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_crowd(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "How busy is the stadium?"}), content_type="application/json")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_parking(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "Where can I park?"}), content_type="application/json")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_accessibility(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "I need wheelchair access"}), content_type="application/json")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_emergency(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "Emergency! Fire!"}), content_type="application/json")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_recycling(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "Where are recycling stations?"}), content_type="application/json")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_with_language(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "Hello", "language": "es"}), content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert "response" in d["data"]

    def test_chat_has_sentiment(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": "I love this stadium!"}), content_type="application/json")
        d = json.loads(r.data)
        assert "sentiment" in d["data"]

    def test_chat_performance(self, client):
        import time
        start = time.time()
        client.post("/api/chat", data=json.dumps({"message": "Hello"}), content_type="application/json")
        elapsed = time.time() - start
        assert elapsed < 5


# ═══ Crowd Management Tests ══════════════════════════════════
class TestCrowd:
    def test_crowd_data(self, client):
        r = client.get("/api/crowd")
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"
        assert "A" in d["data"]

    def test_crowd_overview(self, client):
        r = client.get("/api/crowd/overview")
        d = json.loads(r.data)
        assert "total_occupancy" in d["data"]
        assert "zones" in d["data"]
        assert "recommendations" in d["data"]

    def test_crowd_heatmap(self, client):
        r = client.get("/api/crowd/heatmap")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)
        assert len(d["data"]) > 0
        assert "density" in d["data"][0]

    def test_crowd_predict(self, client):
        r = client.get("/api/crowd/predict?minutes=30")
        d = json.loads(r.data)
        assert "A" in d["data"]


# ═══ IoT Sensor Tests ═════════════════════════════════════════
class TestIoT:
    def test_sensor_readings(self, client):
        r = client.get("/api/iot/sensors")
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"

    def test_zone_summaries(self, client):
        r = client.get("/api/iot/zones")
        d = json.loads(r.data)
        assert "A" in d["data"]

    def test_anomaly_detection(self, client):
        r = client.get("/api/iot/anomalies")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)


# ═══ Emergency System Tests ═══════════════════════════════════
class TestEmergency:
    def test_safety_status(self, client):
        r = client.get("/api/emergency/status")
        d = json.loads(r.data)
        assert "alert_level" in d["data"]
        assert "safety_score" in d["data"]

    def test_raise_incident(self, client):
        r = client.post("/api/emergency/raise",
            data=json.dumps({"type": "medical", "location": {"zone": "A"}}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert "incident" in d["data"]
        assert "protocol" in d["data"]

    def test_resolve_incident(self, client):
        r = client.post("/api/emergency/raise",
            data=json.dumps({"type": "fire", "location": {"zone": "B"}}),
            content_type="application/json")
        inc_id = json.loads(r.data)["data"]["incident"]["id"]
        r2 = client.post("/api/emergency/resolve",
            data=json.dumps({"id": inc_id, "notes": "Resolved"}),
            content_type="application/json")
        assert json.loads(r2.data)["data"]["resolved"]

    def test_evacuation_plan(self, client):
        r = client.post("/api/emergency/evacuation",
            data=json.dumps({"zones": ["A", "C"]}),
            content_type="application/json")
        d = json.loads(r.data)
        assert "evacuation_routes" in d["data"] or "primary_exits" in d["data"]


# ═══ Navigation Tests ═════════════════════════════════════════
class TestNavigation:
    def test_directions(self, client):
        r = client.post("/api/navigation",
            data=json.dumps({"origin": "E1", "destination": "R1"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert "steps" in d["data"]
        assert "estimated_time_min" in d["data"]

    def test_accessible_route(self, client):
        r = client.post("/api/navigation",
            data=json.dumps({"origin": "E1", "destination": "R1", "mode": "accessible"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["data"]["mode"] == "accessible"

    def test_crowd_aware_route(self, client):
        r = client.post("/api/navigation",
            data=json.dumps({"origin": "E1", "destination": "R1", "mode": "crowd_aware"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_nearby_facilities(self, client):
        r = client.post("/api/navigation/nearby",
            data=json.dumps({"lat": 40.8128, "lon": -74.0745, "type": "restrooms"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)

    def test_accessibility_profile(self, client):
        r = client.get("/api/navigation/accessibility/wheelchair")
        d = json.loads(r.data)
        assert "accessible_facilities" in d["data"]


# ═══ Analytics Tests ══════════════════════════════════════════
class TestAnalytics:
    def test_predict_demand(self, client):
        r = client.get("/api/analytics/predict?zone=A&minutes=60")
        d = json.loads(r.data)
        assert "predicted_flow_per_min" in d["data"]

    def test_risk_assessment(self, client):
        r = client.get("/api/analytics/risks")
        d = json.loads(r.data)
        assert "A" in d["data"]

    def test_wait_times(self, client):
        r = client.get("/api/analytics/waits")
        d = json.loads(r.data)
        assert "food_court" in d["data"]

    def test_insights(self, client):
        r = client.get("/api/analytics/insights")
        d = json.loads(r.data)
        assert "optimization_suggestions" in d["data"]


# ═══ Sentiment Tests ══════════════════════════════════════════
class TestSentiment:
    def test_analyze_positive(self, client):
        r = client.post("/api/sentiment/analyze",
            data=json.dumps({"text": "This stadium is amazing! Best experience ever!"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["data"]["sentiment"] == "positive"

    def test_analyze_negative(self, client):
        r = client.post("/api/sentiment/analyze",
            data=json.dumps({"text": "Terrible service, very disappointed and angry"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["data"]["sentiment"] == "negative"

    def test_summary(self, client):
        r = client.get("/api/sentiment/summary")
        d = json.loads(r.data)
        assert "average_score" in d["data"]

    def test_chart_data(self, client):
        r = client.get("/api/sentiment/chart")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)


# ═══ Dashboard Tests ══════════════════════════════════════════
class TestDashboard:
    def test_kpis(self, client):
        r = client.get("/api/dashboard/kpis")
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_hourly(self, client):
        r = client.get("/api/dashboard/hourly")
        d = json.loads(r.data)
        assert "hourly_data" in d["data"]

    def test_revenue(self, client):
        r = client.get("/api/dashboard/revenue")
        d = json.loads(r.data)
        assert "total_revenue" in d["data"]

    def test_staff(self, client):
        r = client.get("/api/dashboard/staff")
        d = json.loads(r.data)
        assert "departments" in d["data"]

    def test_command_center(self, client):
        r = client.get("/api/dashboard/command")
        d = json.loads(r.data)
        assert "kpis" in d["data"]
        assert "alerts" in d["data"]
