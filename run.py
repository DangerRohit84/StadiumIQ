"""Entry point."""
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

from app import create_app

config_name = os.getenv("FLASK_ENV", "development")
if config_name not in ("development", "production"):
    config_name = "development"

app, socketio = create_app(config_name)

if __name__ == "__main__":
    socketio.run(app, debug=app.config["DEBUG"], host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
