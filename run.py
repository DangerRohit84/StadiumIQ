"""Entry point."""
import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

from app import create_app

app, socketio = create_app("development")

if __name__ == "__main__":
    socketio.run(app, debug=app.config["DEBUG"], port=5000)
