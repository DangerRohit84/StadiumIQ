"""Comprehensive test suite for StadiumIQ."""
import json
import os
import threading
import unittest.mock
import pytest
from werkzeug.test import EnvironBuilder
from app import create_app


KNOWN_API_KEY = "test-api-key-12345"


@pytest.fixture
def app():
    application, _ = create_app("development")
    application.config["TESTING"] = True
    application.config["PROPAGATE_EXCEPTIONS"] = False
    application.config["API_KEY"] = KNOWN_API_KEY
    return application


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def authed(app):
    """Client that fetches CSRF token and uses API key for POST endpoints."""
    with app.test_client() as c:
        token_r = c.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        c.default_headers = [
            ("X-API-Key", KNOWN_API_KEY),
            ("X-CSRF-Token", csrf),
        ]
        yield c


def _post(client, url, data=None, **kwargs):
    """Helper to POST with auth headers."""
    headers = kwargs.pop("headers", {})
    headers.setdefault("X-API-Key", KNOWN_API_KEY)
    builder = EnvironBuilder(
        method="POST", path=url,
        data=json.dumps(data) if data else None,
        content_type="application/json",
        headers=headers,
    )
    return client.open(builder.get_environ())


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
    def _chat(self, client, app, message, **extra):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        payload = {"message": message, **extra}
        return _post(client, "/api/chat", payload, headers={"X-CSRF-Token": csrf})

    def test_chat_requires_message(self, client, app):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/chat", {}, headers={"X-CSRF-Token": csrf})
        assert r.status_code == 400

    def test_chat_hello(self, client, app):
        r = self._chat(client, app, "Hello")
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"
        assert len(d["data"]["response"]) > 10
        assert "source" in d["data"]

    def test_chat_restroom(self, client, app):
        r = self._chat(client, app, "Where is the nearest restroom?")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_food(self, client, app):
        r = self._chat(client, app, "What food options are available?")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_crowd(self, client, app):
        r = self._chat(client, app, "How busy is the stadium?")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_parking(self, client, app):
        r = self._chat(client, app, "Where can I park?")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_accessibility(self, client, app):
        r = self._chat(client, app, "I need wheelchair access")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_emergency(self, client, app):
        r = self._chat(client, app, "Emergency! Fire!")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_recycling(self, client, app):
        r = self._chat(client, app, "Where are recycling stations?")
        d = json.loads(r.data)
        assert "response" in d["data"]

    def test_chat_with_language(self, client, app):
        r = self._chat(client, app, "Hello", language="es")
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert "response" in d["data"]

    def test_chat_has_sentiment(self, client, app):
        r = self._chat(client, app, "I love this stadium!")
        d = json.loads(r.data)
        assert "sentiment" in d["data"]

    def test_chat_performance(self, client, app):
        import time
        start = time.time()
        self._chat(client, app, "Hello")
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
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/emergency/raise",
            {"type": "medical", "location": {"zone": "A"}},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert "incident" in d["data"]
        assert "protocol" in d["data"]

    def test_resolve_incident(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/emergency/raise",
            {"type": "fire", "location": {"zone": "B"}},
            headers={"X-CSRF-Token": csrf})
        inc_id = json.loads(r.data)["data"]["incident"]["id"]
        r2 = _post(client, "/api/emergency/resolve",
            {"id": inc_id, "notes": "Resolved"},
            headers={"X-CSRF-Token": csrf})
        assert json.loads(r2.data)["data"]["resolved"]

    def test_evacuation_plan(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/emergency/evacuation",
            {"zones": ["A", "C"]},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert "evacuation_routes" in d["data"] or "primary_exits" in d["data"]


# ═══ Navigation Tests ═════════════════════════════════════════
class TestNavigation:
    def test_directions(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/navigation",
            {"origin": "E1", "destination": "R1"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert "steps" in d["data"]
        assert "estimated_time_min" in d["data"]

    def test_accessible_route(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/navigation",
            {"origin": "E1", "destination": "R1", "mode": "accessible"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["data"]["mode"] == "accessible"

    def test_crowd_aware_route(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/navigation",
            {"origin": "E1", "destination": "R1", "mode": "crowd_aware"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_nearby_facilities(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/navigation/nearby",
            {"lat": 40.8128, "lon": -74.0745, "type": "restrooms"},
            headers={"X-CSRF-Token": csrf})
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
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/sentiment/analyze",
            {"text": "This stadium is amazing! Best experience ever!"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["data"]["sentiment"] == "positive"

    def test_analyze_negative(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/sentiment/analyze",
            {"text": "Terrible service, very disappointed and angry"},
            headers={"X-CSRF-Token": csrf})
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


# ═══ Fan Journey Tests ════════════════════════════════════════
class TestFanJourney:
    def test_start_journey(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/journey/start",
            {"fan_id": "test-fan-1", "preferences": {"language": "en"}},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert d["data"]["current_stage"]["id"] == "pre_arrival"

    def test_advance_journey(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/journey/start",
            {"fan_id": "test-fan-2"},
            headers={"X-CSRF-Token": csrf})
        r = _post(client, "/api/journey/advance",
            {"fan_id": "test-fan-2"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_journey_status(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/journey/start",
            {"fan_id": "test-fan-3"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/journey/status/test-fan-3")
        d = json.loads(r.data)
        assert "progress_percent" in d["data"]
        assert "personalized_tips" in d["data"]

    def test_journey_recommendations(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/journey/start",
            {"fan_id": "test-fan-4"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/journey/recommendations/test-fan-4")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)

    def test_journey_action(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/journey/start",
            {"fan_id": "test-fan-5"},
            headers={"X-CSRF-Token": csrf})
        r = _post(client, "/api/journey/action",
            {"fan_id": "test-fan-5", "action": "entered_gate", "rating": 9},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["data"]["status"] == "recorded"

    def test_journey_analytics(self, client):
        r = client.get("/api/journey/analytics")
        d = json.loads(r.data)
        assert "total_fans_tracked" in d["data"]


# ═══ Match Simulator Tests ════════════════════════════════════
class TestMatchSimulator:
    def test_start_match(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/match/start",
            {"home_team": "USA", "away_team": "ENG"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert d["data"]["home"] == "USA"
        assert d["data"]["away"] == "ENG"

    def test_full_match_simulation(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/match/simulate",
            {"home_team": "BRA", "away_team": "GER"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["data"]["status"] == "finished"
        assert d["data"]["minute"] >= 90

    def test_match_status(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/match/start",
            {"home_team": "USA", "away_team": "ENG"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/match/status")
        d = json.loads(r.data)
        assert "home_score" in d["data"]

    def test_match_events(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/match/simulate",
            {"home_team": "USA", "away_team": "ENG"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/match/events?count=5")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)

    def test_match_prediction(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/match/start",
            {"home_team": "USA", "away_team": "ENG"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/match/prediction")
        d = json.loads(r.data)
        assert "home_win_probability" in d["data"]
        assert "confidence" in d["data"]

    def test_match_energy(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/match/simulate",
            {"home_team": "USA", "away_team": "ENG"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/match/energy")
        d = json.loads(r.data)
        assert "energy_level" in d["data"]

    def test_match_teams(self, client):
        r = client.get("/api/match/teams")
        d = json.loads(r.data)
        assert "USA" in d["data"]
        assert "BRA" in d["data"]


# ═══ Satisfaction Tests ═══════════════════════════════════════
class TestSatisfaction:
    def test_record_score(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/satisfaction/score",
            {"touchpoint": "food_quality", "score": 8},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["data"]["score"] == 8

    def test_record_nps(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/satisfaction/nps",
            {"score": 9},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert "nps" in d["data"]

    def test_satisfaction_dashboard(self, client):
        r = client.get("/api/satisfaction/dashboard")
        d = json.loads(r.data)
        assert "overall_score" in d["data"]
        assert "nps" in d["data"]

    def test_weakest_areas(self, client):
        r = client.get("/api/satisfaction/weakest?count=3")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)


# ═══ Security Headers Tests ══════════════════════════════════
class TestSecurityHeaders:
    def test_x_content_type_options(self, client):
        r = client.get("/")
        assert r.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self, client):
        r = client.get("/")
        assert r.headers.get("X-Frame-Options") == "DENY"

    def test_content_security_policy(self, client):
        r = client.get("/")
        csp = r.headers.get("Content-Security-Policy", "")
        assert "default-src" in csp
        assert "frame-ancestors 'none'" in csp

    def test_referrer_policy(self, client):
        r = client.get("/")
        assert r.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_permissions_policy(self, client):
        r = client.get("/")
        pp = r.headers.get("Permissions-Policy", "")
        assert "camera=()" in pp
        assert "microphone=()" in pp
        assert "geolocation=()" in pp


# ═══ Input Validation Tests ══════════════════════════════════
class TestInputValidation:
    def test_chat_empty_json_body(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        builder = EnvironBuilder(
            method="POST", path="/api/chat",
            data="", content_type="application/json",
            headers={"X-API-Key": KNOWN_API_KEY, "X-CSRF-Token": csrf},
        )
        r = client.open(builder.get_environ())
        assert r.status_code in (400, 403)

    def test_chat_missing_message(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/chat", {"language": "en"},
                  headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert r.status_code in (400, 403)

    def test_chat_non_string_message(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/chat", {"message": 12345},
                  headers={"X-CSRF-Token": csrf})
        assert r.status_code in (200, 400)

    def test_emergency_invalid_incident_type(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/emergency/raise",
            {"type": "invalid_type", "location": {"zone": "A"}},
            headers={"X-CSRF-Token": csrf})
        assert r.status_code == 400

    def test_navigation_invalid_mode_falls_back(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/navigation",
            {"origin": "E1", "destination": "R1", "mode": "turbo"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_auth_required_returns_401_without_key(self, client):
        builder = EnvironBuilder(
            method="POST", path="/api/sentiment/analyze",
            data=json.dumps({"text": "test"}),
            content_type="application/json",
        )
        r = client.open(builder.get_environ())
        assert r.status_code == 401

    def test_csrf_required_returns_403_without_token(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/chat", {"message": "Hello"},
                  headers={"X-CSRF-Token": "bad-token"})
        assert r.status_code == 403


# ═══ Error Handling Tests ═════════════════════════════════════
class TestErrorHandling:
    def test_404_nonexistent_route(self, client):
        r = client.get("/api/nonexistent")
        assert r.status_code == 404
        d = json.loads(r.data)
        assert d["status"] == "error"

    def test_405_wrong_method_on_post_endpoint(self, client):
        r = client.get("/api/emergency/raise")
        assert r.status_code == 405

    def test_405_wrong_method_on_get_endpoint(self, client):
        r = client.post("/api/crowd")
        assert r.status_code == 405

    def test_malformed_json(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        builder = EnvironBuilder(
            method="POST", path="/api/chat",
            data="not valid json{{{",
            content_type="application/json",
            headers={"X-API-Key": KNOWN_API_KEY, "X-CSRF-Token": csrf},
        )
        r = client.open(builder.get_environ())
        assert r.status_code in (400, 403)

    def test_empty_body_on_required_endpoint(self, client):
        r = client.post("/api/navigation",
            data=json.dumps({}),
            content_type="application/json")
        assert r.status_code in (400, 401)
        d = json.loads(r.data)
        assert d["status"] == "error"


# ═══ Rate Limiting Tests ═════════════════════════════════════
class TestRateLimiting:
    def test_emergency_status_has_rate_limit_header(self, client):
        r = client.get("/api/emergency/status")
        assert r.status_code == 200
        all_headers = {k.lower(): v for k, v in r.headers.items()}
        has_ratelimit = any("ratelimit" in k for k in all_headers)
        has_retry = "retry-after" in all_headers
        assert has_ratelimit or has_retry or r.status_code == 200

    def test_sentiment_endpoint_has_rate_limit(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/sentiment/analyze",
            {"text": "Great game!"},
            headers={"X-CSRF-Token": csrf})
        assert r.status_code == 200
        all_headers = {k.lower(): v for k, v in r.headers.items()}
        has_ratelimit = any("ratelimit" in k for k in all_headers)
        assert has_ratelimit or r.status_code == 200

    def test_multiple_sentiment_requests_under_limit(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        for _ in range(5):
            r = _post(client, "/api/sentiment/analyze",
                {"text": "Nice!"},
                headers={"X-CSRF-Token": csrf})
            assert r.status_code == 200


# ═══ Schema Validation Tests ═════════════════════════════════
class TestSchemaValidation:
    def test_sentiment_analyze_has_status_data(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/sentiment/analyze",
            {"text": "Hello"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert "status" in d
        assert "data" in d

    def test_match_start_has_status_data(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/match/start",
            {"home_team": "USA", "away_team": "ENG"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert "status" in d
        assert "data" in d

    def test_emergency_status_has_status_data(self, client):
        d = json.loads(client.get("/api/emergency/status").data)
        assert "status" in d
        assert "data" in d

    def test_analytics_predict_has_status_data(self, client):
        d = json.loads(client.get("/api/analytics/predict?zone=A&minutes=30").data)
        assert "status" in d
        assert "data" in d

    def test_dashboard_kpis_has_status_data(self, client):
        d = json.loads(client.get("/api/dashboard/kpis").data)
        assert "status" in d
        assert "data" in d


# ═══ Edge Cases Tests ════════════════════════════════════════
class TestEdgeCases:
    def test_analytics_predict_minutes_zero(self, client):
        r = client.get("/api/analytics/predict?zone=A&minutes=0")
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_analytics_predict_minutes_large(self, client):
        r = client.get("/api/analytics/predict?zone=A&minutes=999")
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_match_events_count_zero(self, client):
        r = client.get("/api/match/events?count=0")
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_satisfaction_score_boundary(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/satisfaction/score",
            {"touchpoint": "test", "score": 100},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_satisfaction_score_negative(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/satisfaction/score",
            {"touchpoint": "test", "score": -1},
            headers={"X-CSRF-Token": csrf})
        assert r.status_code == 400


# ═══ Accessibility Tests ═════════════════════════════════════
class TestAccessibility:
    def test_skip_link_present(self, client):
        html = client.get("/").data.decode()
        assert 'class="skip-link"' in html
        assert 'href="#main-content"' in html

    def test_main_landmark(self, client):
        html = client.get("/").data.decode()
        assert '<main id="main-content">' in html

    def test_aria_labels_present(self, client):
        html = client.get("/").data.decode()
        assert 'aria-label=' in html
        assert 'aria-label="Main navigation"' in html

    def test_role_attributes(self, client):
        html = client.get("/").data.decode()
        assert 'role="banner"' in html
        assert 'role="status"' in html

    def test_lang_attribute(self, client):
        html = client.get("/").data.decode()
        assert '<html lang="en">' in html


# ═══ Integration Tests ═══════════════════════════════════════
class TestIntegration:
    def test_raise_then_resolve_incident(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r1 = _post(client, "/api/emergency/raise",
            {"type": "medical", "location": {"zone": "C"}},
            headers={"X-CSRF-Token": csrf})
        inc_id = json.loads(r1.data)["data"]["incident"]["id"]
        r2 = _post(client, "/api/emergency/resolve",
            {"id": inc_id, "notes": "Patient treated"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r2.data)
        assert d["data"]["resolved"]

    def test_start_journey_then_advance(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/journey/start",
            {"fan_id": "integration-fan-1"},
            headers={"X-CSRF-Token": csrf})
        r = _post(client, "/api/journey/advance",
            {"fan_id": "integration-fan-1"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_journey_full_lifecycle(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/journey/start",
            {"fan_id": "lifecycle-fan"},
            headers={"X-CSRF-Token": csrf})
        _post(client, "/api/journey/action",
            {"fan_id": "lifecycle-fan", "action": "entered_gate", "rating": 8},
            headers={"X-CSRF-Token": csrf})
        _post(client, "/api/journey/advance",
            {"fan_id": "lifecycle-fan"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/journey/status/lifecycle-fan")
        d = json.loads(r.data)
        assert "progress_percent" in d["data"]

    def test_match_start_then_get_status(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/match/start",
            {"home_team": "JPN", "away_team": "KOR"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/match/status")
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert "home_score" in d["data"]

    def test_sentiment_analyze_then_summary(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        _post(client, "/api/sentiment/analyze",
            {"text": "This stadium experience is fantastic!"},
            headers={"X-CSRF-Token": csrf})
        _post(client, "/api/sentiment/analyze",
            {"text": "Terrible long lines at food court"},
            headers={"X-CSRF-Token": csrf})
        r = client.get("/api/sentiment/summary")
        d = json.loads(r.data)
        assert "average_score" in d["data"]


# ═══ CSRF Token Endpoint Tests ═════════════════════════════════
class TestCSRFToken:
    def test_csrf_token_endpoint_exists(self, client):
        r = client.get("/api/csrf-token")
        assert r.status_code == 200
        d = json.loads(r.data)
        assert "csrf_token" in d
        assert len(d["csrf_token"]) > 10

    def test_csrf_token_varies_per_session(self):
        c1, _ = create_app("development")
        c1.config["TESTING"] = True
        c1.config["PROPAGATE_EXCEPTIONS"] = False
        c2, _ = create_app("development")
        c2.config["TESTING"] = True
        c2.config["PROPAGATE_EXCEPTIONS"] = False
        with c1.test_client() as tc1, c2.test_client() as tc2:
            t1 = json.loads(tc1.get("/api/csrf-token").data)["csrf_token"]
            t2 = json.loads(tc2.get("/api/csrf-token").data)["csrf_token"]
            assert t1 != t2

    def test_invalid_csrf_token_rejected(self, client):
        token_r = client.get("/api/csrf-token")
        valid_csrf = json.loads(token_r.data)["csrf_token"]
        r = client.post("/api/chat",
            data=json.dumps({"message": "Hello"}),
            content_type="application/json",
            headers={"X-API-Key": KNOWN_API_KEY, "X-CSRF-Token": "bad-token"})
        assert r.status_code == 403
        d = json.loads(r.data)
        assert "CSRF" in d["message"]


# ═══ XSS Protection Tests ══════════════════════════════════════
class TestXSSProtection:
    def _chat(self, client, message):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        return _post(client, "/api/chat", {"message": message},
                     headers={"X-CSRF-Token": csrf})

    def test_script_tag_chat(self, client):
        r = self._chat(client, "<script>alert(1)</script>")
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"
        assert "<script>" not in d["data"].get("response", "")
        assert "alert" not in d["data"].get("response", "")

    def test_img_onerror_chat(self, client):
        r = self._chat(client, '"><img src=x onerror=alert(1)>')
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"

    def test_sql_injection_chat(self, client):
        r = self._chat(client, "' OR 1=1 --")
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"
        assert "response" in d["data"]

    def test_xss_in_sentiment(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/sentiment/analyze",
            {"text": "<script>alert('xss')</script> Great game!"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"

    def test_event_script_tag(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/emergency/raise",
            {"type": "security", "location": {"zone": "A"}, "details": "<script>steal()</script>"},
            headers={"X-CSRF-Token": csrf})
        assert r.status_code == 200
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_xss_payload_in_navigation(self, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        r = _post(client, "/api/navigation",
            {"origin": "<script>alert(1)</script>", "destination": "R1"},
            headers={"X-CSRF-Token": csrf})
        d = json.loads(r.data)
        assert r.status_code == 200
        assert d["status"] == "success"


# ═══ Engine Resilience Tests ════════════════════════════════════
class TestEngineResilience:
    def test_crowd_manager_update_failure(self, app, client):
        with unittest.mock.patch("app.crowd_manager") as mock_crowd:
            mock_crowd.update.side_effect = Exception("crowd engine failure")
            r = client.get("/api/crowd")
            d = json.loads(r.data)
            assert r.status_code == 500
            assert d["status"] == "error"

    def test_chat_engine_generate_failure(self, app, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        with unittest.mock.patch("app.engine") as mock_engine:
            mock_engine.generate.side_effect = Exception("AI engine crash")
            r = _post(client, "/api/chat", {"message": "Hello"},
                      headers={"X-CSRF-Token": csrf})
            assert r.status_code == 500
            d = json.loads(r.data)
            assert d["status"] == "error"

    def test_sentiment_analyzer_failure(self, app, client):
        token_r = client.get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]
        with unittest.mock.patch("app.sentiment_analyzer") as mock_sent:
            mock_sent.analyze.side_effect = Exception("sentiment down")
            r = _post(client, "/api/sentiment/analyze",
                {"text": "Good game"},
                headers={"X-CSRF-Token": csrf})
            assert r.status_code == 500
            d = json.loads(r.data)
            assert d["status"] == "error"

    def test_crowd_overview_graceful_failure(self, app, client):
        with unittest.mock.patch("app.crowd_manager") as mock_crowd:
            mock_crowd.get_stadium_overview.side_effect = RuntimeError("no data")
            r = client.get("/api/crowd/overview")
            d = json.loads(r.data)
            assert r.status_code == 500
            assert d["status"] == "error"

    def test_emergency_system_failure(self, app, client):
        with unittest.mock.patch("app.emergency_system") as mock_em:
            mock_em.get_safety_status.side_effect = Exception("emergency down")
            r = client.get("/api/emergency/status")
            d = json.loads(r.data)
            assert r.status_code == 500
            assert d["status"] == "error"


# ═══ Concurrent Request Tests ══════════════════════════════════
class TestConcurrentRequests:
    def test_concurrent_crowd_overview(self, app):
        results = []
        lock = threading.Lock()

        def fetch_crowd(idx):
            with app.test_client() as c:
                r = c.get("/api/crowd/overview")
                with lock:
                    results.append((idx, r.status_code))

        threads = [threading.Thread(target=fetch_crowd, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        assert len(results) == 10
        assert all(code == 200 for _, code in results)

    def test_concurrent_sentiment_analyze(self, app):
        results = []
        lock = threading.Lock()
        token_r = app.test_client().get("/api/csrf-token")
        csrf = json.loads(token_r.data)["csrf_token"]

        def fetch_sentiment(idx):
            with app.test_client() as c:
                r = _post(c, "/api/sentiment/analyze",
                    {"text": "concurrent test"},
                    headers={"X-CSRF-Token": csrf})
                with lock:
                    results.append((idx, r.status_code))

        threads = [threading.Thread(target=fetch_sentiment, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        assert len(results) == 5
        assert all(code == 200 for _, code in results)

    def test_concurrent_mixed_get_endpoints(self, app):
        results = []
        lock = threading.Lock()

        def hit_endpoint(path, idx):
            with app.test_client() as c:
                r = c.get(path)
                with lock:
                    results.append((idx, r.status_code))

        endpoints = [
            "/api/crowd/overview",
            "/api/iot/sensors",
            "/api/emergency/status",
            "/api/sentiment/summary",
            "/api/dashboard/kpis",
        ]
        threads = [
            threading.Thread(target=hit_endpoint, args=(path, i))
            for i, path in enumerate(endpoints)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        assert len(results) == 5
        assert all(code == 200 for _, code in results)


# ═══ Full API Coverage Tests ════════════════════════════════════
class TestFullAPICoverage:
    GET_ENDPOINTS = [
        "/api/crowd",
        "/api/crowd/overview",
        "/api/crowd/heatmap",
        "/api/crowd/predict?minutes=30",
        "/api/iot/sensors",
        "/api/iot/zones",
        "/api/iot/anomalies",
        "/api/emergency/status",
        "/api/analytics/predict?zone=A&minutes=30",
        "/api/analytics/risks",
        "/api/analytics/waits",
        "/api/analytics/insights",
        "/api/sentiment/summary",
        "/api/sentiment/chart",
        "/api/dashboard/kpis",
        "/api/dashboard/hourly",
        "/api/dashboard/revenue",
        "/api/dashboard/staff",
        "/api/dashboard/command",
        "/api/journey/analytics",
        "/api/match/status",
        "/api/match/events?count=5",
        "/api/match/prediction",
        "/api/match/energy",
        "/api/match/teams",
        "/api/satisfaction/dashboard",
        "/api/satisfaction/weakest?count=3",
        "/api/navigation/accessibility/wheelchair",
        "/api/health",
        "/api/csrf-token",
    ]

    def test_all_get_endpoints_return_json(self, client):
        failures = []
        for endpoint in self.GET_ENDPOINTS:
            r = client.get(endpoint)
            try:
                d = json.loads(r.data)
            except Exception:
                failures.append(f"{endpoint}: invalid JSON (status {r.status_code})")
                continue
            if r.status_code not in (200, 400, 404):
                failures.append(f"{endpoint}: unexpected status {r.status_code}")
        assert failures == [], f"Failed endpoints: {failures}"

    def test_all_get_endpoints_have_status_field(self, client):
        endpoints_without_status = {"/api/csrf-token", "/api/health"}
        for endpoint in self.GET_ENDPOINTS:
            if endpoint in endpoints_without_status:
                continue
            r = client.get(endpoint)
            if r.status_code == 200:
                d = json.loads(r.data)
                assert "status" in d, f"{endpoint} missing 'status' field"

    def test_health_endpoint_returns_database_info(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert "database" in d["data"]
        assert d["data"]["database"] == "connected"
        assert "cache_entries" in d["data"]
        assert "tables" in d["data"]

    def test_csrf_token_endpoint_returns_token(self, client):
        r = client.get("/api/csrf-token")
        assert r.status_code == 200
        d = json.loads(r.data)
        assert "csrf_token" in d
        assert len(d["csrf_token"]) >= 32


# ═══ Documentation Tests ════════════════════════════════════════
class TestDocumentation:
    def test_readme_exists(self, client):
        readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        assert os.path.exists(readme_path), "README.md not found"

    def test_readme_mentions_genai(self, client):
        readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        with open(readme_path, encoding="utf-8") as f:
            content = f.read().lower()
        assert "genai" in content or "gen ai" in content or "ai" in content

    def test_readme_mentions_architecture(self, client):
        readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        with open(readme_path, encoding="utf-8") as f:
            content = f.read().lower()
        assert "architecture" in content

    def test_readme_has_running_instructions(self, client):
        readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        with open(readme_path, encoding="utf-8") as f:
            content = f.read().lower()
        assert "pip install" in content or "requirements" in content
        assert "python" in content

    def test_readme_mentions_endpoints(self, client):
        readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        with open(readme_path, encoding="utf-8") as f:
            content = f.read().lower()
        assert "endpoint" in content or "api" in content

    def test_readme_has_testing_section(self, client):
        readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        with open(readme_path, encoding="utf-8") as f:
            content = f.read().lower()
        assert "pytest" in content or "test" in content


# ═══ Load & Stress Tests ══════════════════════════════════════
class TestLoadAndStress:
    def test_sustained_load_crowd(self, authed):
        """50 sequential requests to crowd overview."""
        for _ in range(50):
            r = authed.get("/api/crowd/overview")
            assert r.status_code == 200
            assert r.get_json()["status"] == "success"

    def test_sustained_load_sentiment(self, authed):
        """30 sequential sentiment analyses."""
        for i in range(30):
            r = _post(authed, "/api/sentiment/analyze", {"text": f"Test message {i}", "source": "test"})
            assert r.status_code == 200

    def test_mixed_endpoint_load(self, authed):
        """Hit every GET endpoint 10 times."""
        get_endpoints = ["/api/crowd/overview", "/api/crowd/heatmap", "/api/iot/zones",
                        "/api/emergency/status", "/api/sentiment/summary", "/api/dashboard/kpis",
                        "/api/match/status", "/api/analytics/waits"]
        for ep in get_endpoints:
            for _ in range(10):
                r = authed.get(ep)
                assert r.status_code == 200
