"""StadiumIQ - GenAI Smart Stadium Assistant for FIFA World Cup 2026."""
import logging
import os
import time
import uuid
import hmac
import hashlib
import secrets as secrets_mod
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit
from config.settings import config_by_name
from core.ai.genai_engine import engine
from core.crowd.crowd_engine import crowd_manager
from core.iot.sensor_engine import sensor_network
from core.emergency.emergency_engine import emergency_system
from core.sentiment.sentiment_engine import sentiment_analyzer
from core.predictive.predictive_engine import predictive_analytics
from core.navigation.nav_engine import navigation_engine
from core.analytics.dashboard_engine import analytics_dashboard
from core.fan import fan_journey
from core.match import match_simulator
from core.satisfaction import satisfaction_tracker
from core.database import db

logger = logging.getLogger("stadiumiq.security")

VALID_ZONES = {"A", "B", "C", "D"}
VALID_MODES = {"standard", "crowd_aware", "accessible", "fastest"}
VALID_STAGES = {"arrival", "entry", "seating", "concession", "halftime", "second_half", "post_match", "departure"}
VALID_INCIDENT_TYPES = {"medical", "fire", "security", "structural", "weather", "crowd_surge", "lost_person", "equipment_failure"}
VALID_FACILITY_TYPES = {"restrooms", "food", "medical", "merchandise", "water_fountain", "atm", "info_desk"}
MAX_CHAT_LENGTH = 2000
MAX_DETAILS_LENGTH = 500
MAX_PAGE_SIZE = 100


def _validate_json(*required_fields):
    """Validate that request has JSON body with required fields."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({"status": "error", "message": "Invalid JSON"}), 400
            for field in required_fields:
                if field not in data:
                    return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400
            return f(*args, **kwargs)
        return decorated
    return decorator


def _sanitize_string(value: str, max_len: int = 500) -> str:
    """Sanitize and truncate string input."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_len]


def require_api_key(f):
    """Decorator that requires a valid X-API-Key header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key", "")
        from flask import current_app
        expected = current_app.config.get("API_KEY", "")
        if not expected or not hmac.compare_digest(api_key, expected):
            return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated


def _generate_csrf_token():
    """Generate a CSRF token and store it in the session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets_mod.token_hex(32)
    return session["_csrf_token"]


def _validate_csrf_token():
    """Validate the CSRF token from the request against the session token.
    Always requires a valid session with a CSRF token for POST /api/chat.
    """
    expected = session.get("_csrf_token")
    if not expected:
        return False
    token = request.headers.get("X-CSRF-Token", "")
    return hmac.compare_digest(token, expected)


def create_app(config_name: str = "development") -> Flask:
    """Application factory with security hardening."""
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
    app.config.from_object(config_by_name[config_name])

    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5000,http://127.0.0.1:5000").split(",")
    CORS(app, origins=allowed_origins, methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-CSRF-Token"])
    limiter = Limiter(get_remote_address, app=app, default_limits=["200 per hour"])
    socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode="threading")

    # ─── HTTPS Redirect (production) ──────────────────────────
    @app.before_request
    def redirect_to_https():
        if not app.config.get("DEBUG") and not request.is_secure and request.headers.get("X-Forwarded-Proto", "http") != "https":
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)

    # ─── CSRF Token Endpoint ──────────────────────────────────
    @app.route("/api/csrf-token", methods=["GET"])
    def get_csrf_token():
        token = _generate_csrf_token()
        return jsonify({"status": "success", "csrf_token": token})

    # ─── Security Headers ──────────────────────────────────────
    @app.after_request
    def set_security_headers(response):
        """Inject security headers into every response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'"
        )
        if not app.config.get("DEBUG"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # ─── Error Handlers ────────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        """Handle malformed requests."""
        return jsonify({"status": "error", "message": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        """Handle missing resource requests."""
        return jsonify({"status": "error", "message": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        """Handle unsupported HTTP methods."""
        return jsonify({"status": "error", "message": "Method not allowed"}), 405

    @app.errorhandler(429)
    def rate_limited(e):
        """Handle rate limit exceeded responses."""
        return jsonify({"status": "error", "message": "Rate limit exceeded"}), 429

    @app.errorhandler(500)
    def server_error(e):
        """Handle unexpected internal server errors."""
        logger.error("Internal server error: %s", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    # ─── Health Check ─────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def api_health():
        """Return system health status including database connectivity."""
        try:
            conn = db._get_conn()
            conn.execute("SELECT 1")
            cache_count = conn.execute("SELECT COUNT(*) as cnt FROM cache").fetchone()['cnt']
            return jsonify({
                "status": "success",
                "data": {
                    "database": "connected",
                    "cache_entries": cache_count,
                    "tables": {
                        "cache": conn.execute("SELECT COUNT(*) as cnt FROM cache").fetchone()['cnt'],
                        "fan_journeys": conn.execute("SELECT COUNT(*) as cnt FROM fan_journeys").fetchone()['cnt'],
                        "incidents": conn.execute("SELECT COUNT(*) as cnt FROM incidents").fetchone()['cnt'],
                        "sentiment_log": conn.execute("SELECT COUNT(*) as cnt FROM sentiment_log").fetchone()['cnt'],
                        "match_events": conn.execute("SELECT COUNT(*) as cnt FROM match_events").fetchone()['cnt'],
                    }
                }
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

    # ─── Pages ────────────────────────────────────────────────
    @app.route("/")
    def index():
        """Render the main fan-facing homepage."""
        return render_template("index.html")

    @app.route("/command-center")
    def command_center():
        """Render the operations command center dashboard."""
        return render_template("index.html")

    # ─── AI Chat ──────────────────────────────────────────────
    @app.route("/api/chat", methods=["POST"])
    @limiter.limit("30 per minute")
    def api_chat():
        """Process a fan chat message and return an AI-generated response."""
        if not _validate_csrf_token():
            return jsonify({"status": "error", "message": "Invalid CSRF token"}), 403

        data = request.get_json(silent=True)
        if not data or "message" not in data:
            return jsonify({"status": "error", "message": "No message"}), 400

        message = _sanitize_string(data["message"], MAX_CHAT_LENGTH)
        if not message:
            return jsonify({"status": "error", "message": "Empty message"}), 400

        user_type = data.get("user_type", "fan")
        language = data.get("language", "en")
        fan_id = data.get("fan_id", "anonymous")
        urgency = "high" if any(w in message.lower() for w in ["emergency", "fire", "help", "danger"]) else "normal"

        context = {
            "stadium": "MetLife Stadium",
            "crowd": crowd_manager.get_stadium_overview(),
            "safety": emergency_system.get_safety_status(),
        }

        result = engine.generate(message, context, language, user_type, urgency, fan_id)
        sentiment = sentiment_analyzer.analyze(message, source="chat")
        result["sentiment"] = sentiment

        socketio.emit("new_message", {
            "user_message": message,
            "ai_response": result["response"],
            "sentiment": sentiment["sentiment"],
            "timestamp": time.time(),
        })

        return jsonify({"status": "success", "data": result})

    # ─── Crowd Management ─────────────────────────────────────
    @app.route("/api/crowd", methods=["GET"])
    def api_crowd():
        """Return updated crowd density readings for all zones."""
        data = crowd_manager.update()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/crowd/overview", methods=["GET"])
    def api_crowd_overview():
        """Return a high-level overview of stadium crowd status."""
        cached = db.cache_get("crowd_overview")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = crowd_manager.get_stadium_overview()
        db.cache_set("crowd_overview", data, ttl=2.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/crowd/heatmap", methods=["GET"])
    def api_crowd_heatmap():
        """Return crowd density heatmap data for visualization."""
        cached = db.cache_get("crowd_heatmap")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = crowd_manager.get_heatmap_data()
        db.cache_set("crowd_heatmap", data, ttl=3.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/crowd/predict", methods=["GET"])
    def api_crowd_predict():
        """Predict crowd flow for the specified number of minutes ahead."""
        minutes = request.args.get("minutes", 30, type=int)
        minutes = max(1, min(minutes, 180))
        data = crowd_manager.predict_flow(minutes)
        return jsonify({"status": "success", "data": data})

    # ─── IoT Sensors ──────────────────────────────────────────
    @app.route("/api/iot/sensors", methods=["GET"])
    def api_iot_sensors():
        """Return updated readings from IoT sensors across the stadium."""
        data = sensor_network.update_readings()
        return jsonify({"status": "success", "data": {k: v for k, v in list(data.items())[:20]}})

    @app.route("/api/iot/zones", methods=["GET"])
    def api_iot_zones():
        """Return aggregated sensor summaries per zone."""
        cached = db.cache_get("iot_zones")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = sensor_network.get_all_zone_summaries()
        db.cache_set("iot_zones", data, ttl=3.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/iot/anomalies", methods=["GET"])
    def api_iot_anomalies():
        """Return sensor readings flagged as anomalies."""
        cached = db.cache_get("iot_anomalies")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = sensor_network.get_anomaly_readings()
        db.cache_set("iot_anomalies", data, ttl=5.0)
        return jsonify({"status": "success", "data": data})

    # ─── Emergency ────────────────────────────────────────────
    @app.route("/api/emergency/raise", methods=["POST"])
    @limiter.limit("10 per minute")
    @require_api_key
    @_validate_json("type")
    def api_emergency_raise():
        """Raise a new emergency incident and broadcast an alert."""
        data = request.get_json()
        inc_type = _sanitize_string(data["type"], 50)
        if inc_type.lower() not in VALID_INCIDENT_TYPES:
            return jsonify({"status": "error", "message": f"Invalid incident type. Valid: {VALID_INCIDENT_TYPES}"}), 400
        details = _sanitize_string(data.get("details", ""), MAX_DETAILS_LENGTH)
        result = emergency_system.raise_incident(inc_type, data.get("location", {}), details)
        logger.warning("Emergency raised: %s by %s", inc_type, request.remote_addr)
        socketio.emit("emergency_alert", result)
        return jsonify({"status": "success", "data": result})

    @app.route("/api/emergency/resolve", methods=["POST"])
    @limiter.limit("10 per minute")
    @require_api_key
    @_validate_json("id")
    def api_emergency_resolve():
        """Resolve an active emergency incident by ID."""
        data = request.get_json()
        inc_id = _sanitize_string(data["id"], 50)
        notes = _sanitize_string(data.get("notes", ""), MAX_DETAILS_LENGTH)
        result = emergency_system.resolve_incident(inc_id, notes)
        logger.warning("Emergency resolved: %s by %s", inc_id, request.remote_addr)
        return jsonify({"status": "success", "data": result})

    @app.route("/api/emergency/status", methods=["GET"])
    def api_emergency_status():
        """Return current safety and alert level status."""
        return jsonify({"status": "success", "data": emergency_system.get_safety_status()})

    @app.route("/api/emergency/evacuation", methods=["POST"])
    @limiter.limit("5 per minute")
    @require_api_key
    def api_emergency_evacuation():
        """Generate an evacuation plan for the specified zones."""
        data = request.get_json(silent=True) or {}
        zones = data.get("zones", ["A"])
        if not isinstance(zones, list):
            zones = ["A"]
        zones = [z for z in zones if z in VALID_ZONES] or ["A"]
        plan = emergency_system.get_evacuation_plan(zones)
        logger.warning("Evacuation plan requested for zones: %s", zones)
        return jsonify({"status": "success", "data": plan})

    # ─── Navigation ───────────────────────────────────────────
    @app.route("/api/navigation", methods=["POST"])
    @limiter.limit("60 per minute")
    @require_api_key
    @_validate_json("origin", "destination")
    def api_navigation():
        """Calculate a route between origin and destination."""
        data = request.get_json()
        origin = _sanitize_string(data["origin"], 100)
        dest = _sanitize_string(data["destination"], 100)
        mode = _sanitize_string(data.get("mode", "standard"), 20)
        if mode not in VALID_MODES:
            mode = "standard"

        if mode == "crowd_aware":
            zones = crowd_manager.get_all_zones()
            route = navigation_engine.get_crowd_aware_route(origin, dest, zones)
        else:
            route = navigation_engine.get_directions(origin, dest, mode)
        return jsonify({"status": "success", "data": route})

    @app.route("/api/navigation/nearby", methods=["POST"])
    @limiter.limit("60 per minute")
    @require_api_key
    def api_navigation_nearby():
        """Find nearby facilities of a given type near coordinates."""
        data = request.get_json(silent=True) or {}
        lat = data.get("lat", 40.8128)
        lon = data.get("lon", -74.0745)
        if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
            lat = 40.8128
        if not isinstance(lon, (int, float)) or not (-180 <= lon <= 180):
            lon = -74.0745
        ftype = _sanitize_string(data.get("type", "restrooms"), 30)
        if ftype not in VALID_FACILITY_TYPES:
            ftype = "restrooms"
        count = data.get("count", 3)
        if not isinstance(count, int) or count < 1:
            count = 3
        count = min(count, MAX_PAGE_SIZE)
        results = navigation_engine.get_nearby_options(lat, lon, ftype, count)
        return jsonify({"status": "success", "data": results})

    @app.route("/api/navigation/accessibility/<profile>", methods=["GET"])
    def api_navigation_accessibility(profile):
        """Return accessibility information for a given profile."""
        profile = _sanitize_string(profile, 30)
        data = navigation_engine.get_accessibility_info(profile)
        return jsonify({"status": "success", "data": data})

    # ─── Predictive Analytics ─────────────────────────────────
    @app.route("/api/analytics/predict", methods=["GET"])
    def api_analytics_predict():
        """Predict service demand for a zone over a time horizon."""
        zone = request.args.get("zone", "A")
        if zone not in VALID_ZONES:
            zone = "A"
        minutes = request.args.get("minutes", 60, type=int)
        minutes = max(1, min(minutes, 180))
        data = predictive_analytics.predict_demand(zone, minutes)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/analytics/risks", methods=["GET"])
    def api_analytics_risks():
        """Assess incident risk levels across all zones."""
        zones = crowd_manager.get_all_zones()
        data = predictive_analytics.predict_incident_risk(zones)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/analytics/waits", methods=["GET"])
    def api_analytics_waits():
        """Predict wait times for concession and restroom facilities."""
        cached = db.cache_get("analytics_waits")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = predictive_analytics.predict_wait_times()
        db.cache_set("analytics_waits", data, ttl=5.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/analytics/insights", methods=["GET"])
    def api_analytics_insights():
        """Generate actionable operational insights from analytics."""
        cached = db.cache_get("analytics_insights")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = predictive_analytics.generate_operational_insights()
        db.cache_set("analytics_insights", data, ttl=10.0)
        return jsonify({"status": "success", "data": data})

    # ─── Sentiment ────────────────────────────────────────────
    @app.route("/api/sentiment/analyze", methods=["POST"])
    @limiter.limit("60 per minute")
    @require_api_key
    def api_sentiment_analyze():
        """Analyze the sentiment of submitted fan feedback text."""
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400
        text = _sanitize_string(data.get("text", ""), MAX_CHAT_LENGTH)
        if not text:
            return jsonify({"status": "error", "message": "No text provided"}), 400
        result = sentiment_analyzer.analyze(text, data.get("source", "chat"))
        return jsonify({"status": "success", "data": result})

    @app.route("/api/sentiment/summary", methods=["GET"])
    def api_sentiment_summary():
        """Return an aggregated summary of fan sentiment."""
        cached = db.cache_get("sentiment_summary")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = sentiment_analyzer.get_feedback_summary()
        db.cache_set("sentiment_summary", data, ttl=5.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/sentiment/chart", methods=["GET"])
    def api_sentiment_chart():
        """Return sentiment data formatted for chart visualization."""
        cached = db.cache_get("sentiment_chart")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = sentiment_analyzer.get_sentiment_chart_data()
        db.cache_set("sentiment_chart", data, ttl=5.0)
        return jsonify({"status": "success", "data": data})

    # ─── Dashboard Analytics ──────────────────────────────────
    @app.route("/api/dashboard/kpis", methods=["GET"])
    def api_dashboard_kpis():
        """Return real-time key performance indicators."""
        cached = db.cache_get("kpis")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = analytics_dashboard.get_realtime_kpis()
        db.cache_set("kpis", data, ttl=3.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/dashboard/hourly", methods=["GET"])
    def api_dashboard_hourly():
        """Return hourly analytics trends."""
        cached = db.cache_get("hourly")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = analytics_dashboard.get_hourly_analytics()
        db.cache_set("hourly", data, ttl=5.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/dashboard/revenue", methods=["GET"])
    def api_dashboard_revenue():
        """Return revenue analytics across concession areas."""
        cached = db.cache_get("revenue")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = analytics_dashboard.get_revenue_analytics()
        db.cache_set("revenue", data, ttl=10.0)
        return jsonify({"status": "success", "data": data})

    # ─── AI Translation ───────────────────────────────────────
    _translation_cache: dict = {}

    @app.route("/api/i18n/translate", methods=["POST"])
    @limiter.limit("20 per minute")
    @require_api_key
    def api_translate():
        """Translate UI strings to the target language via GenAI."""
        data = request.get_json(silent=True)
        if not data or "texts" not in data or "target_lang" not in data:
            return jsonify({"status": "error", "message": "texts and target_lang required"}), 400

        texts = data["texts"]
        target_lang = data["target_lang"]

        if not isinstance(texts, dict) or not texts:
            return jsonify({"status": "error", "message": "texts must be a non-empty dict"}), 400
        if len(texts) > 100:
            return jsonify({"status": "error", "message": "Max 100 texts per request"}), 400

        cache_key = f"{target_lang}:{hash(frozenset(texts.items()))}"
        if cache_key in _translation_cache:
            return jsonify({"status": "success", "data": _translation_cache[cache_key], "cached": True})

        lang_names = {
            "es": "Spanish", "fr": "French", "de": "German", "ar": "Arabic",
            "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "pt": "Portuguese", "hi": "Hindi"
        }
        lang_name = lang_names.get(target_lang, target_lang)

        prompt_parts = [f"Translate these UI strings to {lang_name}. Return ONLY a valid JSON object with the same keys and translated values. No markdown, no explanation.\n"]
        prompt_parts.append("{")
        for key, val in texts.items():
            escaped_val = val.replace('"', '\\"')
            prompt_parts.append(f'  "{key}": "{escaped_val}",')
        prompt_parts.append("}")

        full_prompt = "\n".join(prompt_parts)

        try:
            response = engine._model.generate_content(full_prompt)
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            import json
            translated = json.loads(raw)
            _translation_cache[cache_key] = translated
            return jsonify({"status": "success", "data": translated, "cached": False})
        except Exception as e:
            logger.error("Translation failed: %s", e)
            return jsonify({"status": "error", "message": "Translation failed"}), 500

    @app.route("/api/dashboard/staff", methods=["GET"])
    def api_dashboard_staff():
        """Return current staff deployment across zones."""
        cached = db.cache_get("staff")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = analytics_dashboard.get_staff_deployment()
        db.cache_set("staff", data, ttl=5.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/dashboard/command", methods=["GET"])
    def api_dashboard_command():
        """Return a consolidated command center summary."""
        data = analytics_dashboard.get_command_center_summary()
        return jsonify({"status": "success", "data": data})

    # ─── Fan Journey ──────────────────────────────────────────
    @app.route("/api/journey/start", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    def api_journey_start():
        """Start a new fan journey session."""
        data = request.get_json(silent=True) or {}
        fan_id = data.get("fan_id", f"fan-{uuid.uuid4().hex[:12]}")
        result = fan_journey.start_journey(fan_id, data.get("preferences"))
        return jsonify({"status": "success", "data": result})

    @app.route("/api/journey/advance", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    @_validate_json("fan_id")
    def api_journey_advance():
        """Advance a fan to the next journey stage."""
        data = request.get_json()
        fan_id = _sanitize_string(data["fan_id"], 50)
        stage = _sanitize_string(data.get("stage", ""), 30)
        if stage and stage not in VALID_STAGES:
            return jsonify({"status": "error", "message": f"Invalid stage. Valid: {VALID_STAGES}"}), 400
        result = fan_journey.advance_stage(fan_id, stage)
        return jsonify({"status": "success", "data": result})

    @app.route("/api/journey/status/<fan_id>", methods=["GET"])
    def api_journey_status(fan_id):
        """Return the current status of a fan's journey."""
        fan_id = _sanitize_string(fan_id, 50)
        result = fan_journey.get_journey_status(fan_id)
        return jsonify({"status": "success", "data": result})

    @app.route("/api/journey/recommendations/<fan_id>", methods=["GET"])
    def api_journey_recommendations(fan_id):
        """Return personalized recommendations for a fan."""
        fan_id = _sanitize_string(fan_id, 50)
        result = fan_journey.get_personalized_recommendations(fan_id)
        return jsonify({"status": "success", "data": result})

    @app.route("/api/journey/action", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    @_validate_json("fan_id", "action")
    def api_journey_action():
        """Record a completed fan action within the journey."""
        data = request.get_json()
        fan_id = _sanitize_string(data["fan_id"], 50)
        action = _sanitize_string(data["action"], 50)
        result = fan_journey.complete_action(fan_id, action, data.get("rating"))
        return jsonify({"status": "success", "data": result})

    @app.route("/api/journey/analytics", methods=["GET"])
    def api_journey_analytics():
        """Return aggregate fan journey analytics."""
        return jsonify({"status": "success", "data": fan_journey.get_analytics()})

    # ─── Match Simulator ──────────────────────────────────────
    @app.route("/api/match/start", methods=["POST"])
    @limiter.limit("10 per minute")
    @require_api_key
    def api_match_start():
        """Start a new match simulation between two teams."""
        data = request.get_json(silent=True) or {}
        home = _sanitize_string(data.get("home_team", "USA"), 30)
        away = _sanitize_string(data.get("away_team", "ENG"), 30)
        result = match_simulator.start_match(home, away)
        return jsonify({"status": "success", "data": result})

    @app.route("/api/match/simulate", methods=["POST"])
    @limiter.limit("10 per minute")
    @require_api_key
    def api_match_simulate():
        """Simulate a complete match from kickoff to final whistle."""
        data = request.get_json(silent=True) or {}
        home = _sanitize_string(data.get("home_team", "USA"), 30)
        away = _sanitize_string(data.get("away_team", "ENG"), 30)
        result = match_simulator.simulate_full_match(home, away)
        return jsonify({"status": "success", "data": result})

    @app.route("/api/match/minute", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    def api_match_minute():
        """Simulate a single minute of match play."""
        result = match_simulator.simulate_minute()
        return jsonify({"status": "success", "data": result})

    @app.route("/api/match/status", methods=["GET"])
    def api_match_status():
        """Return the current match state and score."""
        cached = db.cache_get("match_status")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = match_simulator.get_match_status()
        db.cache_set("match_status", data, ttl=2.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/match/events", methods=["GET"])
    def api_match_events():
        """Return recent match events such as goals and cards."""
        count = request.args.get("count", 5, type=int)
        count = max(1, min(count, MAX_PAGE_SIZE))
        return jsonify({"status": "success", "data": match_simulator.get_recent_events(count)})

    @app.route("/api/match/prediction", methods=["GET"])
    def api_match_prediction():
        """Return a win/draw/loss prediction for the current match."""
        cached = db.cache_get("match_prediction")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = match_simulator.get_prediction()
        db.cache_set("match_prediction", data, ttl=5.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/match/energy", methods=["GET"])
    def api_match_energy():
        """Return the current crowd energy level during the match."""
        cached = db.cache_get("match_energy")
        if cached:
            return jsonify({"status": "success", "data": cached, "cached": True})
        data = match_simulator.get_crowd_energy()
        db.cache_set("match_energy", data, ttl=2.0)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/match/teams", methods=["GET"])
    def api_match_teams():
        """Return the list of available teams for match simulation."""
        return jsonify({"status": "success", "data": match_simulator.TEAMS})

    # ─── Satisfaction ─────────────────────────────────────────
    @app.route("/api/satisfaction/score", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    @_validate_json("touchpoint", "score")
    def api_satisfaction_score():
        """Record a fan satisfaction score for a touchpoint."""
        data = request.get_json()
        tp = _sanitize_string(data["touchpoint"], 50)
        score = data.get("score")
        if not isinstance(score, (int, float)) or not (0 <= score <= 100):
            return jsonify({"status": "error", "message": "Score must be a number 0-100"}), 400
        result = satisfaction_tracker.record_score(tp, score, data.get("fan_id"))
        return jsonify({"status": "success", "data": result})

    @app.route("/api/satisfaction/nps", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    @_validate_json("score")
    def api_satisfaction_nps():
        """Record a Net Promoter Score from a fan."""
        data = request.get_json()
        score = data.get("score")
        if not isinstance(score, (int, float)) or not (0 <= score <= 10):
            return jsonify({"status": "error", "message": "NPS score must be 0-10"}), 400
        result = satisfaction_tracker.record_nps(score, data.get("fan_id"))
        return jsonify({"status": "success", "data": result})

    @app.route("/api/satisfaction/dashboard", methods=["GET"])
    def api_satisfaction_dashboard():
        """Return the satisfaction tracker dashboard data."""
        return jsonify({"status": "success", "data": satisfaction_tracker.get_dashboard_data()})

    @app.route("/api/satisfaction/weakest", methods=["GET"])
    def api_satisfaction_weakest():
        """Return the weakest satisfaction areas needing improvement."""
        count = request.args.get("count", 3, type=int)
        count = max(1, min(count, 13))
        return jsonify({"status": "success", "data": satisfaction_tracker.get_weakest_areas(count)})

    # ─── WebSocket Events ─────────────────────────────────────
    @socketio.on("connect")
    def handle_connect():
        """Acknowledge a new WebSocket client connection."""
        emit("connected", {"status": "online", "timestamp": time.time()})

    @socketio.on("request_update")
    def handle_update_request():
        """Push current crowd and sensor data to the requesting client."""
        emit("crowd_update", crowd_manager.get_all_zones())
        emit("sensor_update", sensor_network.get_all_zone_summaries())

    def background_updates():
        """Periodically push crowd and sensor updates to all clients."""
        cache_counter = 0
        while True:
            socketio.sleep(5)
            try:
                crowd_data = crowd_manager.update()
                socketio.emit("crowd_update", crowd_data)
                sensor_data = sensor_network.update_readings()
                anomalies = sensor_network.get_anomaly_readings()
                if anomalies:
                    socketio.emit("anomaly_alert", {"anomalies": anomalies})
                cache_counter += 5
                if cache_counter >= 30:
                    db.cache_clear()
                    cache_counter = 0
            except Exception as e:
                logger.error("Background update error: %s", e)

    socketio.start_background_task(background_updates)

    return app, socketio


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    app, socketio = create_app("development")
    socketio.run(app, debug=app.config["DEBUG"], port=5000)
