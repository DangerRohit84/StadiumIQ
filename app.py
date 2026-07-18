"""StadiumIQ - GenAI Smart Stadium Assistant for FIFA World Cup 2026."""
import time
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
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


def create_app(config_name: str = "development") -> Flask:
    """Application factory with full feature integration."""
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
    app.config.from_object(config_by_name[config_name])
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    # ─── Pages ────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/command-center")
    def command_center():
        return render_template("index.html")

    # ─── AI Chat ──────────────────────────────────────────────
    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"status": "error", "message": "No message"}), 400

        user_type = data.get("user_type", "fan")
        language = data.get("language", "en")
        urgency = "high" if any(w in data["message"].lower() for w in ["emergency", "fire", "help", "danger"]) else "normal"

        context = {
            "stadium": "MetLife Stadium",
            "crowd": crowd_manager.get_stadium_overview(),
            "safety": emergency_system.get_safety_status(),
        }

        result = engine.generate(data["message"], context, language, user_type, urgency)

        sentiment = sentiment_analyzer.analyze(data["message"], source="chat")
        result["sentiment"] = sentiment

        socketio.emit("new_message", {
            "user_message": data["message"],
            "ai_response": result["response"],
            "sentiment": sentiment["sentiment"],
            "timestamp": time.time(),
        })

        return jsonify({"status": "success", "data": result})

    # ─── Crowd Management ─────────────────────────────────────
    @app.route("/api/crowd", methods=["GET"])
    def api_crowd():
        data = crowd_manager.update()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/crowd/overview", methods=["GET"])
    def api_crowd_overview():
        data = crowd_manager.get_stadium_overview()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/crowd/heatmap", methods=["GET"])
    def api_crowd_heatmap():
        data = crowd_manager.get_heatmap_data()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/crowd/predict", methods=["GET"])
    def api_crowd_predict():
        minutes = request.args.get("minutes", 30, type=int)
        data = crowd_manager.predict_flow(minutes)
        return jsonify({"status": "success", "data": data})

    # ─── IoT Sensors ──────────────────────────────────────────
    @app.route("/api/iot/sensors", methods=["GET"])
    def api_iot_sensors():
        data = sensor_network.update_readings()
        return jsonify({"status": "success", "data": {k: v for k, v in list(data.items())[:20]}})

    @app.route("/api/iot/zones", methods=["GET"])
    def api_iot_zones():
        data = sensor_network.get_all_zone_summaries()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/iot/anomalies", methods=["GET"])
    def api_iot_anomalies():
        data = sensor_network.get_anomaly_readings()
        return jsonify({"status": "success", "data": data})

    # ─── Emergency ────────────────────────────────────────────
    @app.route("/api/emergency/raise", methods=["POST"])
    def api_emergency_raise():
        data = request.get_json()
        if not data or "type" not in data:
            return jsonify({"status": "error", "message": "Incident type required"}), 400
        result = emergency_system.raise_incident(data["type"], data.get("location", {}), data.get("details", ""))
        socketio.emit("emergency_alert", result)
        return jsonify({"status": "success", "data": result})

    @app.route("/api/emergency/resolve", methods=["POST"])
    def api_emergency_resolve():
        data = request.get_json()
        result = emergency_system.resolve_incident(data.get("id", ""), data.get("notes", ""))
        return jsonify({"status": "success", "data": result})

    @app.route("/api/emergency/status", methods=["GET"])
    def api_emergency_status():
        return jsonify({"status": "success", "data": emergency_system.get_safety_status()})

    @app.route("/api/emergency/evacuation", methods=["POST"])
    def api_emergency_evacuation():
        data = request.get_json()
        zones = data.get("zones", ["A"])
        plan = emergency_system.get_evacuation_plan(zones)
        return jsonify({"status": "success", "data": plan})

    # ─── Navigation ───────────────────────────────────────────
    @app.route("/api/navigation", methods=["POST"])
    def api_navigation():
        data = request.get_json()
        origin = data.get("origin")
        dest = data.get("destination")
        mode = data.get("mode", "standard")
        if not origin or not dest:
            return jsonify({"status": "error", "message": "Origin and destination required"}), 400

        if mode == "crowd_aware":
            zones = crowd_manager.get_all_zones()
            route = navigation_engine.get_crowd_aware_route(origin, dest, zones)
        else:
            route = navigation_engine.get_directions(origin, dest, mode)
        return jsonify({"status": "success", "data": route})

    @app.route("/api/navigation/nearby", methods=["POST"])
    def api_navigation_nearby():
        data = request.get_json()
        lat = data.get("lat", 40.8128)
        lon = data.get("lon", -74.0745)
        ftype = data.get("type", "restrooms")
        count = data.get("count", 3)
        results = navigation_engine.get_nearby_options(lat, lon, ftype, count)
        return jsonify({"status": "success", "data": results})

    @app.route("/api/navigation/accessibility/<profile>", methods=["GET"])
    def api_navigation_accessibility(profile):
        data = navigation_engine.get_accessibility_info(profile)
        return jsonify({"status": "success", "data": data})

    # ─── Predictive Analytics ─────────────────────────────────
    @app.route("/api/analytics/predict", methods=["GET"])
    def api_analytics_predict():
        zone = request.args.get("zone", "A")
        minutes = request.args.get("minutes", 60, type=int)
        data = predictive_analytics.predict_demand(zone, minutes)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/analytics/risks", methods=["GET"])
    def api_analytics_risks():
        zones = crowd_manager.get_all_zones()
        data = predictive_analytics.predict_incident_risk(zones)
        return jsonify({"status": "success", "data": data})

    @app.route("/api/analytics/waits", methods=["GET"])
    def api_analytics_waits():
        data = predictive_analytics.predict_wait_times()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/analytics/insights", methods=["GET"])
    def api_analytics_insights():
        data = predictive_analytics.generate_operational_insights()
        return jsonify({"status": "success", "data": data})

    # ─── Sentiment ────────────────────────────────────────────
    @app.route("/api/sentiment/analyze", methods=["POST"])
    def api_sentiment_analyze():
        data = request.get_json()
        text = data.get("text", "")
        result = sentiment_analyzer.analyze(text, data.get("source", "chat"))
        return jsonify({"status": "success", "data": result})

    @app.route("/api/sentiment/summary", methods=["GET"])
    def api_sentiment_summary():
        data = sentiment_analyzer.get_feedback_summary()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/sentiment/chart", methods=["GET"])
    def api_sentiment_chart():
        data = sentiment_analyzer.get_sentiment_chart_data()
        return jsonify({"status": "success", "data": data})

    # ─── Dashboard Analytics ──────────────────────────────────
    @app.route("/api/dashboard/kpis", methods=["GET"])
    def api_dashboard_kpis():
        data = analytics_dashboard.get_realtime_kpis()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/dashboard/hourly", methods=["GET"])
    def api_dashboard_hourly():
        data = analytics_dashboard.get_hourly_analytics()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/dashboard/revenue", methods=["GET"])
    def api_dashboard_revenue():
        data = analytics_dashboard.get_revenue_analytics()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/dashboard/staff", methods=["GET"])
    def api_dashboard_staff():
        data = analytics_dashboard.get_staff_deployment()
        return jsonify({"status": "success", "data": data})

    @app.route("/api/dashboard/command", methods=["GET"])
    def api_dashboard_command():
        data = analytics_dashboard.get_command_center_summary()
        return jsonify({"status": "success", "data": data})

    # ─── WebSocket Events ─────────────────────────────────────
    @socketio.on("connect")
    def handle_connect():
        emit("connected", {"status": "online", "timestamp": time.time()})

    @socketio.on("request_update")
    def handle_update_request():
        emit("crowd_update", crowd_manager.get_all_zones())
        emit("sensor_update", sensor_network.get_all_zone_summaries())

    def background_updates():
        while True:
            socketio.sleep(5)
            crowd_data = crowd_manager.update()
            socketio.emit("crowd_update", crowd_data)
            sensor_data = sensor_network.update_readings()
            anomalies = sensor_network.get_anomaly_readings()
            if anomalies:
                socketio.emit("anomaly_alert", {"anomalies": anomalies})

    socketio.start_background_task(background_updates)

    return app


if __name__ == "__main__":
    app = create_app("development")
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    socketio.run(app, debug=True, port=5000)
