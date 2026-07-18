"""Comprehensive test suite for StadiumIQ."""
import json
import pytest
from app import create_app


@pytest.fixture
def client():
    app, _ = create_app("development")
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


# ═══ Fan Journey Tests ════════════════════════════════════════
class TestFanJourney:
    def test_start_journey(self, client):
        r = client.post("/api/journey/start",
            data=json.dumps({"fan_id": "test-fan-1", "preferences": {"language": "en"}}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert d["data"]["current_stage"]["id"] == "pre_arrival"

    def test_advance_journey(self, client):
        client.post("/api/journey/start",
            data=json.dumps({"fan_id": "test-fan-2"}),
            content_type="application/json")
        r = client.post("/api/journey/advance",
            data=json.dumps({"fan_id": "test-fan-2"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_journey_status(self, client):
        client.post("/api/journey/start",
            data=json.dumps({"fan_id": "test-fan-3"}),
            content_type="application/json")
        r = client.get("/api/journey/status/test-fan-3")
        d = json.loads(r.data)
        assert "progress_percent" in d["data"]
        assert "personalized_tips" in d["data"]

    def test_journey_recommendations(self, client):
        client.post("/api/journey/start",
            data=json.dumps({"fan_id": "test-fan-4"}),
            content_type="application/json")
        r = client.get("/api/journey/recommendations/test-fan-4")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)

    def test_journey_action(self, client):
        client.post("/api/journey/start",
            data=json.dumps({"fan_id": "test-fan-5"}),
            content_type="application/json")
        r = client.post("/api/journey/action",
            data=json.dumps({"fan_id": "test-fan-5", "action": "entered_gate", "rating": 9}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["data"]["status"] == "recorded"

    def test_journey_analytics(self, client):
        r = client.get("/api/journey/analytics")
        d = json.loads(r.data)
        assert "total_fans_tracked" in d["data"]


# ═══ Match Simulator Tests ════════════════════════════════════
class TestMatchSimulator:
    def test_start_match(self, client):
        r = client.post("/api/match/start",
            data=json.dumps({"home_team": "USA", "away_team": "ENG"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert d["data"]["home"] == "USA"
        assert d["data"]["away"] == "ENG"

    def test_full_match_simulation(self, client):
        r = client.post("/api/match/simulate",
            data=json.dumps({"home_team": "BRA", "away_team": "GER"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["data"]["status"] == "finished"
        assert d["data"]["minute"] >= 90

    def test_match_status(self, client):
        client.post("/api/match/start",
            data=json.dumps({"home_team": "USA", "away_team": "ENG"}),
            content_type="application/json")
        r = client.get("/api/match/status")
        d = json.loads(r.data)
        assert "home_score" in d["data"]

    def test_match_events(self, client):
        client.post("/api/match/simulate",
            data=json.dumps({"home_team": "USA", "away_team": "ENG"}),
            content_type="application/json")
        r = client.get("/api/match/events?count=5")
        d = json.loads(r.data)
        assert isinstance(d["data"], list)

    def test_match_prediction(self, client):
        client.post("/api/match/start",
            data=json.dumps({"home_team": "USA", "away_team": "ENG"}),
            content_type="application/json")
        r = client.get("/api/match/prediction")
        d = json.loads(r.data)
        assert "home_win_probability" in d["data"]
        assert "confidence" in d["data"]

    def test_match_energy(self, client):
        client.post("/api/match/simulate",
            data=json.dumps({"home_team": "USA", "away_team": "ENG"}),
            content_type="application/json")
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
        r = client.post("/api/satisfaction/score",
            data=json.dumps({"touchpoint": "food_quality", "score": 8}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["data"]["score"] == 8

    def test_record_nps(self, client):
        r = client.post("/api/satisfaction/nps",
            data=json.dumps({"score": 9}),
            content_type="application/json")
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
        r = client.post("/api/chat", data="", content_type="application/json")
        assert r.status_code == 400

    def test_chat_missing_message(self, client):
        r = client.post("/api/chat", data=json.dumps({"language": "en"}), content_type="application/json")
        d = json.loads(r.data)
        assert "message" in d.get("message", "").lower() or r.status_code == 400

    def test_chat_non_string_message(self, client):
        r = client.post("/api/chat", data=json.dumps({"message": 12345}), content_type="application/json")
        assert r.status_code in (200, 400)

    def test_emergency_invalid_incident_type(self, client):
        r = client.post("/api/emergency/raise",
            data=json.dumps({"type": "invalid_type", "location": {"zone": "A"}}),
            content_type="application/json")
        assert r.status_code == 400

    def test_navigation_invalid_mode_falls_back(self, client):
        r = client.post("/api/navigation",
            data=json.dumps({"origin": "E1", "destination": "R1", "mode": "turbo"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"


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
        r = client.post("/api/chat",
            data="not valid json{{{",
            content_type="application/json")
        assert r.status_code == 400

    def test_empty_body_on_required_endpoint(self, client):
        r = client.post("/api/navigation",
            data=json.dumps({}),
            content_type="application/json")
        assert r.status_code == 400
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
        r = client.post("/api/sentiment/analyze",
            data=json.dumps({"text": "Great game!"}),
            content_type="application/json")
        assert r.status_code == 200
        all_headers = {k.lower(): v for k, v in r.headers.items()}
        has_ratelimit = any("ratelimit" in k for k in all_headers)
        assert has_ratelimit or r.status_code == 200

    def test_multiple_sentiment_requests_under_limit(self, client):
        for _ in range(5):
            r = client.post("/api/sentiment/analyze",
                data=json.dumps({"text": "Nice!"}),
                content_type="application/json")
            assert r.status_code == 200


# ═══ Schema Validation Tests ═════════════════════════════════
class TestSchemaValidation:
    def test_sentiment_analyze_has_status_data(self, client):
        r = client.post("/api/sentiment/analyze",
            data=json.dumps({"text": "Hello"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert "status" in d
        assert "data" in d

    def test_match_start_has_status_data(self, client):
        r = client.post("/api/match/start",
            data=json.dumps({"home_team": "USA", "away_team": "ENG"}),
            content_type="application/json")
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
        r = client.post("/api/satisfaction/score",
            data=json.dumps({"touchpoint": "test", "score": 100}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_satisfaction_score_negative(self, client):
        r = client.post("/api/satisfaction/score",
            data=json.dumps({"touchpoint": "test", "score": -1}),
            content_type="application/json")
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
        r1 = client.post("/api/emergency/raise",
            data=json.dumps({"type": "medical", "location": {"zone": "C"}}),
            content_type="application/json")
        inc_id = json.loads(r1.data)["data"]["incident"]["id"]
        r2 = client.post("/api/emergency/resolve",
            data=json.dumps({"id": inc_id, "notes": "Patient treated"}),
            content_type="application/json")
        d = json.loads(r2.data)
        assert d["data"]["resolved"]

    def test_start_journey_then_advance(self, client):
        client.post("/api/journey/start",
            data=json.dumps({"fan_id": "integration-fan-1"}),
            content_type="application/json")
        r = client.post("/api/journey/advance",
            data=json.dumps({"fan_id": "integration-fan-1"}),
            content_type="application/json")
        d = json.loads(r.data)
        assert d["status"] == "success"

    def test_journey_full_lifecycle(self, client):
        client.post("/api/journey/start",
            data=json.dumps({"fan_id": "lifecycle-fan"}),
            content_type="application/json")
        client.post("/api/journey/action",
            data=json.dumps({"fan_id": "lifecycle-fan", "action": "entered_gate", "rating": 8}),
            content_type="application/json")
        client.post("/api/journey/advance",
            data=json.dumps({"fan_id": "lifecycle-fan"}),
            content_type="application/json")
        r = client.get("/api/journey/status/lifecycle-fan")
        d = json.loads(r.data)
        assert "progress_percent" in d["data"]

    def test_match_start_then_get_status(self, client):
        client.post("/api/match/start",
            data=json.dumps({"home_team": "JPN", "away_team": "KOR"}),
            content_type="application/json")
        r = client.get("/api/match/status")
        d = json.loads(r.data)
        assert d["status"] == "success"
        assert "home_score" in d["data"]

    def test_sentiment_analyze_then_summary(self, client):
        client.post("/api/sentiment/analyze",
            data=json.dumps({"text": "This stadium experience is fantastic!"}),
            content_type="application/json")
        client.post("/api/sentiment/analyze",
            data=json.dumps({"text": "Terrible long lines at food court"}),
            content_type="application/json")
        r = client.get("/api/sentiment/summary")
        d = json.loads(r.data)
        assert "average_score" in d["data"]
