"""StadiumIQ - GenAI Smart Stadium Assistant for FIFA World Cup 2026."""
import logging
import os
import time
import uuid
import hmac
import secrets as secrets_mod
from functools import wraps
from typing import Any, Callable
from flask import Flask, Response, g, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from flask_compress import Compress
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


def cached_endpoint(ttl: float = 5.0) -> Callable:
    """Cache GET endpoint responses with TTL."""
    def decorator(f: Callable) -> Callable:
        """Wrap function with caching logic."""
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Execute function with cache check."""
            cache_key = f"{request.path}:{request.query_string.decode()}"
            try:
                cached = db.cache_get(cache_key)
            except Exception:
                cached = None
            if cached:
                return jsonify({"status": "success", "data": cached, "cached": True})
            result = f(*args, **kwargs)
            if result.status_code == 200:
                data = result.get_json().get("data") if hasattr(result, 'get_json') else None
                if data:
                    try:
                        db.cache_set(cache_key, data, ttl=ttl)
                    except Exception:
                        pass
            return result
        return wrapper
    return decorator


def _validate_json(*required_fields: str) -> Callable:
    """Validate that request has JSON body with required fields."""
    def decorator(f: Callable) -> Callable:
        """Wrap function with JSON validation."""
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            """Validate JSON body before calling function."""
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


def require_api_key(f: Callable) -> Callable:
    """Decorator that requires a valid X-API-Key header and CSRF token."""
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        """Check API key and CSRF token before calling function."""
        api_key = request.headers.get("X-API-Key", "")
        from flask import current_app
        expected = current_app.config.get("API_KEY", "")
        if not expected or not hmac.compare_digest(api_key, expected):
            return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
        if not _validate_csrf_token():
            return jsonify({"status": "error", "message": "Invalid CSRF token"}), 403
        return f(*args, **kwargs)
    return decorated


def require_csrf(f: Callable) -> Callable:
    """Decorator that requires only a valid CSRF token (for web UI endpoints)."""
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        """Check CSRF token before calling function."""
        if not _validate_csrf_token():
            return jsonify({"status": "error", "message": "Invalid CSRF token"}), 403
        return f(*args, **kwargs)
    return decorated


def _generate_csrf_token() -> str:
    """Generate a CSRF token and store it in the session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets_mod.token_hex(32)
    return session["_csrf_token"]


def _validate_csrf_token() -> bool:
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
    Compress(app)
    limiter = Limiter(get_remote_address, app=app, default_limits=["200 per hour"])
    socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode="threading")

    @app.before_request
    def set_nonce() -> None:
        """Generate a per-request CSP nonce for the template."""
        g.nonce = secrets_mod.token_urlsafe(16)

    # ─── HTTPS Redirect (production) ──────────────────────────
    @app.before_request
    def redirect_to_https() -> None:
        """Redirect HTTP requests to HTTPS in production."""
        if not app.config.get("DEBUG") and not request.is_secure and request.headers.get("X-Forwarded-Proto", "http") != "https":
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)

    # ─── CSRF Token Endpoint ──────────────────────────────────
    @app.route("/api/csrf-token", methods=["GET"])
    def get_csrf_token() -> tuple:
        """Return a CSRF token for the current session."""
        try:
            token = _generate_csrf_token()
            return jsonify({"status": "success", "csrf_token": token})
        except Exception as e:
            logger.error("Route get_csrf_token failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Security Headers ──────────────────────────────────────
    @app.after_request
    def set_security_headers(response) -> Response:
        """Inject security headers into every response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        nonce = g.nonce
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.socket.io; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'"
        )
        if not app.config.get("DEBUG"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        return response

    # ─── Error Handlers ────────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e) -> tuple:
        """Handle malformed requests."""
        return jsonify({"status": "error", "message": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(e) -> tuple:
        """Handle missing resource requests."""
        return jsonify({"status": "error", "message": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e) -> tuple:
        """Handle unsupported HTTP methods."""
        return jsonify({"status": "error", "message": "Method not allowed"}), 405

    @app.errorhandler(429)
    def rate_limited(e) -> tuple:
        """Handle rate limit exceeded responses."""
        response = jsonify({"status": "error", "message": "Rate limit exceeded"})
        response.status_code = 429
        response.headers["Retry-After"] = "60"
        return response

    @app.errorhandler(500)
    def server_error(e) -> tuple:
        """Handle unexpected internal server errors."""
        logger.error("Internal server error: %s", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    # ─── Health Check ─────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def api_health() -> tuple:
        """Return system health status including database connectivity."""
        try:
            cached = db.cache_get("health")
            if cached:
                return jsonify({"status": "success", "data": cached, "cached": True})
            conn = db._get_conn()
            conn.execute("SELECT 1")
            cache_count = conn.execute("SELECT COUNT(*) as cnt FROM cache").fetchone()['cnt']
            health_data = {
                "database": "connected",
                "cache_entries": cache_count,
                "tables": {
                    "cache": cache_count,
                    "fan_journeys": conn.execute("SELECT COUNT(*) as cnt FROM fan_journeys").fetchone()['cnt'],
                    "incidents": conn.execute("SELECT COUNT(*) as cnt FROM incidents").fetchone()['cnt'],
                    "sentiment_log": conn.execute("SELECT COUNT(*) as cnt FROM sentiment_log").fetchone()['cnt'],
                    "match_events": conn.execute("SELECT COUNT(*) as cnt FROM match_events").fetchone()['cnt'],
                }
            }
            db.cache_set("health", health_data, ttl=10)
            return jsonify({"status": "success", "data": health_data})
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return jsonify({"status": "error", "message": "Service unavailable"}), 500

    # ─── Pages ────────────────────────────────────────────────
    @app.route("/")
    def index() -> str:
        """Render the main fan-facing homepage."""
        try:
            return render_template("index.html")
        except Exception as e:
            logger.error("Route index failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/command-center")
    def command_center() -> str:
        """Render the operations command center dashboard."""
        try:
            return render_template("index.html")
        except Exception as e:
            logger.error("Route command_center failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── AI Chat ──────────────────────────────────────────────
    @app.route("/api/chat", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_csrf
    def api_chat() -> tuple:
        """Process a fan chat message and return an AI-generated response."""
        try:
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
        except Exception as e:
            logger.error("Route api_chat failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Crowd Management ─────────────────────────────────────
    @app.route("/api/crowd", methods=["GET"])
    @cached_endpoint(ttl=2)
    def api_crowd() -> tuple:
        """Return updated crowd density readings for all zones."""
        try:
            data = crowd_manager.update()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_crowd failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/crowd/overview", methods=["GET"])
    @cached_endpoint(ttl=2.0)
    def api_crowd_overview() -> tuple:
        """Return a high-level overview of stadium crowd status."""
        try:
            data = crowd_manager.get_stadium_overview()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_crowd_overview failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/crowd/heatmap", methods=["GET"])
    @cached_endpoint(ttl=3.0)
    def api_crowd_heatmap() -> tuple:
        """Return crowd density heatmap data for visualization."""
        try:
            data = crowd_manager.get_heatmap_data()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_crowd_heatmap failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/crowd/predict", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_crowd_predict() -> tuple:
        """Predict crowd flow for the specified number of minutes ahead."""
        try:
            minutes = request.args.get("minutes", 30, type=int)
            minutes = max(1, min(minutes, 180))
            data = crowd_manager.predict_flow(minutes)
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_crowd_predict failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── IoT Sensors ──────────────────────────────────────────
    @app.route("/api/iot/sensors", methods=["GET"])
    @cached_endpoint(ttl=2)
    def api_iot_sensors() -> tuple:
        """Return updated readings from IoT sensors across the stadium."""
        try:
            data = sensor_network.update_readings()
            limited = {k: v for k, v in list(data.items())[:20]}
            return jsonify({"status": "success", "data": limited})
        except Exception as e:
            logger.error("Route api_iot_sensors failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/iot/zones", methods=["GET"])
    @cached_endpoint(ttl=3.0)
    def api_iot_zones() -> tuple:
        """Return aggregated sensor summaries per zone."""
        try:
            data = sensor_network.get_all_zone_summaries()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_iot_zones failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/iot/anomalies", methods=["GET"])
    @cached_endpoint(ttl=5.0)
    def api_iot_anomalies() -> tuple:
        """Return sensor readings flagged as anomalies."""
        try:
            data = sensor_network.get_anomaly_readings()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_iot_anomalies failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Emergency ────────────────────────────────────────────
    @app.route("/api/emergency/raise", methods=["POST"])
    @limiter.limit("10 per minute")
    @require_api_key
    @_validate_json("type")
    def api_emergency_raise() -> tuple:
        """Raise a new emergency incident and broadcast an alert."""
        try:
            data = request.get_json()
            inc_type = _sanitize_string(data["type"], 50)
            if inc_type.lower() not in VALID_INCIDENT_TYPES:
                return jsonify({"status": "error", "message": f"Invalid incident type. Valid: {VALID_INCIDENT_TYPES}"}), 400
            details = _sanitize_string(data.get("details", ""), MAX_DETAILS_LENGTH)
            result = emergency_system.raise_incident(inc_type, data.get("location", {}), details)
            logger.warning("Emergency raised: %s by %s", inc_type, request.remote_addr)
            socketio.emit("emergency_alert", result)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_emergency_raise failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/emergency/resolve", methods=["POST"])
    @limiter.limit("10 per minute")
    @require_api_key
    @_validate_json("id")
    def api_emergency_resolve() -> tuple:
        """Resolve an active emergency incident by ID."""
        try:
            data = request.get_json()
            inc_id = _sanitize_string(data["id"], 50)
            notes = _sanitize_string(data.get("notes", ""), MAX_DETAILS_LENGTH)
            result = emergency_system.resolve_incident(inc_id, notes)
            logger.warning("Emergency resolved: %s by %s", inc_id, request.remote_addr)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_emergency_resolve failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/emergency/status", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_emergency_status() -> tuple:
        """Return current safety and alert level status."""
        try:
            data = emergency_system.get_safety_status()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_emergency_status failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/emergency/evacuation", methods=["POST"])
    @limiter.limit("5 per minute")
    @require_api_key
    def api_emergency_evacuation() -> tuple:
        """Generate an evacuation plan for the specified zones."""
        try:
            data = request.get_json(silent=True) or {}
            zones = data.get("zones", ["A"])
            if not isinstance(zones, list):
                zones = ["A"]
            zones = [z for z in zones if z in VALID_ZONES] or ["A"]
            plan = emergency_system.get_evacuation_plan(zones)
            logger.warning("Evacuation plan requested for zones: %s", zones)
            return jsonify({"status": "success", "data": plan})
        except Exception as e:
            logger.error("Route api_emergency_evacuation failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Navigation ───────────────────────────────────────────
    @app.route("/api/navigation", methods=["POST"])
    @limiter.limit("60 per minute")
    @require_api_key
    @_validate_json("origin", "destination")
    def api_navigation() -> tuple:
        """Calculate a route between origin and destination."""
        try:
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
        except Exception as e:
            logger.error("Route api_navigation failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/navigation/nearby", methods=["POST"])
    @limiter.limit("60 per minute")
    @require_api_key
    def api_navigation_nearby() -> tuple:
        """Find nearby facilities of a given type near coordinates."""
        try:
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
        except Exception as e:
            logger.error("Route api_navigation_nearby failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/navigation/accessibility/<profile>", methods=["GET"])
    @cached_endpoint(ttl=60)
    def api_navigation_accessibility(profile) -> tuple:
        """Return accessibility information for a given profile."""
        try:
            profile = _sanitize_string(profile, 30)
            data = navigation_engine.get_accessibility_info(profile)
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_navigation_accessibility failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Predictive Analytics ─────────────────────────────────
    @app.route("/api/analytics/predict", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_analytics_predict() -> tuple:
        """Predict service demand for a zone over a time horizon."""
        try:
            zone = request.args.get("zone", "A")
            if zone not in VALID_ZONES:
                zone = "A"
            minutes = request.args.get("minutes", 60, type=int)
            minutes = max(1, min(minutes, 180))
            data = predictive_analytics.predict_demand(zone, minutes)
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_analytics_predict failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/analytics/risks", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_analytics_risks() -> tuple:
        """Assess incident risk levels across all zones."""
        try:
            zones = crowd_manager.get_all_zones()
            data = predictive_analytics.predict_incident_risk(zones)
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_analytics_risks failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/analytics/waits", methods=["GET"])
    @cached_endpoint(ttl=5.0)
    def api_analytics_waits() -> tuple:
        """Predict wait times for concession and restroom facilities."""
        try:
            data = predictive_analytics.predict_wait_times()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_analytics_waits failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/analytics/insights", methods=["GET"])
    @cached_endpoint(ttl=10.0)
    def api_analytics_insights() -> tuple:
        """Generate actionable operational insights from analytics."""
        try:
            data = predictive_analytics.generate_operational_insights()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_analytics_insights failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Sentiment ────────────────────────────────────────────
    @app.route("/api/sentiment/analyze", methods=["POST"])
    @limiter.limit("60 per minute")
    @require_api_key
    def api_sentiment_analyze() -> tuple:
        """Analyze the sentiment of submitted fan feedback text."""
        try:
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"status": "error", "message": "Invalid JSON"}), 400
            text = _sanitize_string(data.get("text", ""), MAX_CHAT_LENGTH)
            if not text:
                return jsonify({"status": "error", "message": "No text provided"}), 400
            result = sentiment_analyzer.analyze(text, data.get("source", "chat"))
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_sentiment_analyze failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/sentiment/summary", methods=["GET"])
    @cached_endpoint(ttl=5.0)
    def api_sentiment_summary() -> tuple:
        """Return an aggregated summary of fan sentiment."""
        try:
            data = sentiment_analyzer.get_feedback_summary()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_sentiment_summary failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/sentiment/chart", methods=["GET"])
    @cached_endpoint(ttl=5.0)
    def api_sentiment_chart() -> tuple:
        """Return sentiment data formatted for chart visualization."""
        try:
            data = sentiment_analyzer.get_sentiment_chart_data()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_sentiment_chart failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Dashboard Analytics ──────────────────────────────────
    @app.route("/api/dashboard/kpis", methods=["GET"])
    @cached_endpoint(ttl=3.0)
    def api_dashboard_kpis() -> tuple:
        """Return real-time key performance indicators."""
        try:
            data = analytics_dashboard.get_realtime_kpis()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_dashboard_kpis failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/dashboard/hourly", methods=["GET"])
    @cached_endpoint(ttl=5.0)
    def api_dashboard_hourly() -> tuple:
        """Return hourly analytics trends."""
        try:
            data = analytics_dashboard.get_hourly_analytics()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_dashboard_hourly failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/dashboard/revenue", methods=["GET"])
    @cached_endpoint(ttl=10.0)
    def api_dashboard_revenue() -> tuple:
        """Return revenue analytics across concession areas."""
        try:
            data = analytics_dashboard.get_revenue_analytics()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_dashboard_revenue failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── AI Translation ───────────────────────────────────────
    _translation_cache: dict = {}
    _MAX_TRANSLATION_CACHE = 500


    def _cache_translation(key, value) -> None:
        """Cache translation with LRU eviction."""
        _translation_cache[key] = value
        if len(_translation_cache) > _MAX_TRANSLATION_CACHE:
            oldest = next(iter(_translation_cache))
            del _translation_cache[oldest]

    @app.route("/api/i18n/translate", methods=["POST"])
    @limiter.limit("20 per minute")
    @require_csrf
    def api_translate() -> tuple:
        """Translate UI strings to the target language via GenAI."""
        try:
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
                raw = engine.generate_text(full_prompt)
                if not raw:
                    return jsonify({"status": "success", "data": texts, "cached": False, "note": "fallback"})
                raw = raw.strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                import json
                translated = json.loads(raw)
                _cache_translation(cache_key, translated)
                return jsonify({"status": "success", "data": translated, "cached": False})
            except Exception as e:
                logger.error("Translation failed: %s", e)
                return jsonify({"status": "success", "data": texts, "cached": False, "note": "fallback"})
        except Exception as e:
            logger.error("Route api_translate failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/dashboard/staff", methods=["GET"])
    @cached_endpoint(ttl=5.0)
    def api_dashboard_staff() -> tuple:
        """Return current staff deployment across zones."""
        try:
            data = analytics_dashboard.get_staff_deployment()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_dashboard_staff failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/dashboard/command", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_dashboard_command() -> tuple:
        """Return a consolidated command center summary."""
        try:
            data = analytics_dashboard.get_command_center_summary()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_dashboard_command failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Fan Journey ──────────────────────────────────────────
    @app.route("/api/journey/start", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    def api_journey_start() -> tuple:
        """Start a new fan journey session."""
        try:
            data = request.get_json(silent=True) or {}
            fan_id = data.get("fan_id", f"fan-{uuid.uuid4().hex[:12]}")
            result = fan_journey.start_journey(fan_id, data.get("preferences"))
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_journey_start failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/journey/advance", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    @_validate_json("fan_id")
    def api_journey_advance() -> tuple:
        """Advance a fan to the next journey stage."""
        try:
            data = request.get_json()
            fan_id = _sanitize_string(data["fan_id"], 50)
            stage = _sanitize_string(data.get("stage", ""), 30)
            if stage and stage not in VALID_STAGES:
                return jsonify({"status": "error", "message": f"Invalid stage. Valid: {VALID_STAGES}"}), 400
            result = fan_journey.advance_stage(fan_id, stage)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_journey_advance failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/journey/status/<fan_id>", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_journey_status(fan_id) -> tuple:
        """Return the current status of a fan's journey."""
        try:
            fan_id = _sanitize_string(fan_id, 50)
            result = fan_journey.get_journey_status(fan_id)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_journey_status failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/journey/recommendations/<fan_id>", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_journey_recommendations(fan_id) -> tuple:
        """Return personalized recommendations for a fan."""
        try:
            fan_id = _sanitize_string(fan_id, 50)
            result = fan_journey.get_personalized_recommendations(fan_id)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_journey_recommendations failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/journey/action", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    @_validate_json("fan_id", "action")
    def api_journey_action() -> tuple:
        """Record a completed fan action within the journey."""
        try:
            data = request.get_json()
            fan_id = _sanitize_string(data["fan_id"], 50)
            action = _sanitize_string(data["action"], 50)
            result = fan_journey.complete_action(fan_id, action, data.get("rating"))
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_journey_action failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/journey/analytics", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_journey_analytics() -> tuple:
        """Return aggregate fan journey analytics."""
        try:
            data = fan_journey.get_analytics()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_journey_analytics failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Match Simulator ──────────────────────────────────────
    @app.route("/api/match/start", methods=["POST"])
    @limiter.limit("10 per minute")
    @require_api_key
    def api_match_start() -> tuple:
        """Start a new match simulation between two teams."""
        try:
            data = request.get_json(silent=True) or {}
            home = _sanitize_string(data.get("home_team", "USA"), 30)
            away = _sanitize_string(data.get("away_team", "ENG"), 30)
            result = match_simulator.start_match(home, away)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_match_start failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/match/simulate", methods=["POST"])
    @limiter.limit("10 per minute")
    @require_api_key
    def api_match_simulate() -> tuple:
        """Simulate a complete match from kickoff to final whistle."""
        try:
            data = request.get_json(silent=True) or {}
            home = _sanitize_string(data.get("home_team", "USA"), 30)
            away = _sanitize_string(data.get("away_team", "ENG"), 30)
            result = match_simulator.simulate_full_match(home, away)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_match_simulate failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/match/minute", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    def api_match_minute() -> tuple:
        """Simulate a single minute of match play."""
        try:
            result = match_simulator.simulate_minute()
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_match_minute failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/match/status", methods=["GET"])
    @cached_endpoint(ttl=2.0)
    def api_match_status() -> tuple:
        """Return the current match state and score."""
        try:
            data = match_simulator.get_match_status()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_match_status failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/match/events", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_match_events() -> tuple:
        """Return recent match events such as goals and cards."""
        try:
            count = request.args.get("count", 5, type=int)
            count = max(1, min(count, MAX_PAGE_SIZE))
            data = match_simulator.get_recent_events(count)
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_match_events failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/match/prediction", methods=["GET"])
    @cached_endpoint(ttl=5.0)
    def api_match_prediction() -> tuple:
        """Return a win/draw/loss prediction for the current match."""
        try:
            data = match_simulator.get_prediction()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_match_prediction failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/match/energy", methods=["GET"])
    @cached_endpoint(ttl=2.0)
    def api_match_energy() -> tuple:
        """Return the current crowd energy level during the match."""
        try:
            data = match_simulator.get_crowd_energy()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_match_energy failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/match/teams", methods=["GET"])
    @cached_endpoint(ttl=60)
    def api_match_teams() -> tuple:
        """Return the list of available teams for match simulation."""
        try:
            data = match_simulator.TEAMS
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_match_teams failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── Satisfaction ─────────────────────────────────────────
    @app.route("/api/satisfaction/score", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    @_validate_json("touchpoint", "score")
    def api_satisfaction_score() -> tuple:
        """Record a fan satisfaction score for a touchpoint."""
        try:
            data = request.get_json()
            tp = _sanitize_string(data["touchpoint"], 50)
            score = data.get("score")
            if not isinstance(score, (int, float)) or not (0 <= score <= 100):
                return jsonify({"status": "error", "message": "Score must be a number 0-100"}), 400
            result = satisfaction_tracker.record_score(tp, score, data.get("fan_id"))
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_satisfaction_score failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/satisfaction/nps", methods=["POST"])
    @limiter.limit("30 per minute")
    @require_api_key
    @_validate_json("score")
    def api_satisfaction_nps() -> tuple:
        """Record a Net Promoter Score from a fan."""
        try:
            data = request.get_json()
            score = data.get("score")
            if not isinstance(score, (int, float)) or not (0 <= score <= 10):
                return jsonify({"status": "error", "message": "NPS score must be 0-10"}), 400
            result = satisfaction_tracker.record_nps(score, data.get("fan_id"))
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Route api_satisfaction_nps failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/satisfaction/dashboard", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_satisfaction_dashboard() -> tuple:
        """Return the satisfaction tracker dashboard data."""
        try:
            data = satisfaction_tracker.get_dashboard_data()
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_satisfaction_dashboard failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    @app.route("/api/satisfaction/weakest", methods=["GET"])
    @cached_endpoint(ttl=5)
    def api_satisfaction_weakest() -> tuple:
        """Return the weakest satisfaction areas needing improvement."""
        try:
            count = request.args.get("count", 3, type=int)
            count = max(1, min(count, 13))
            data = satisfaction_tracker.get_weakest_areas(count)
            return jsonify({"status": "success", "data": data})
        except Exception as e:
            logger.error("Route api_satisfaction_weakest failed: %s", e)
            return jsonify({"status": "error", "message": "Internal error"}), 500

    # ─── WebSocket Events ─────────────────────────────────────
    @socketio.on("connect")
    def handle_connect() -> None:
        """Acknowledge a new WebSocket client connection."""
        try:
            emit("connected", {"status": "online", "timestamp": time.time()})
        except Exception as e:
            logger.error("WebSocket handle_connect failed: %s", e)

    @socketio.on("request_update")
    def handle_update_request() -> None:
        """Push current crowd and sensor data to the requesting client."""
        try:
            emit("crowd_update", crowd_manager.get_all_zones())
            emit("sensor_update", sensor_network.get_all_zone_summaries())
        except Exception as e:
            logger.error("WebSocket handle_update_request failed: %s", e)

    def background_updates() -> None:
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
                    try:
                        db.cache_clear()
                    except Exception:
                        pass
                    cache_counter = 0
            except Exception as e:
                logger.error("Background update error: %s", e)

    socketio.start_background_task(background_updates)

    return app, socketio


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    app, socketio = create_app("development")
    socketio.run(app, debug=app.config["DEBUG"], port=5000)
