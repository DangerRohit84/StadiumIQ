"""Pytest configuration to suppress known external warnings and prevent background tasks."""
import warnings
from unittest.mock import patch

warnings.filterwarnings(
    "ignore",
    message="You are using a Python version",
    category=FutureWarning,
)
warnings.filterwarnings(
    "ignore",
    message=".*google.generativeai.*",
    category=FutureWarning,
)
warnings.filterwarnings(
    "ignore",
    message="unclosed file",
    category=ResourceWarning,
)


def pytest_configure(config):
    """Patch socketio.start_background_task to prevent background threads during tests."""
    _noop = lambda *a, **kw: None
    patch("flask_socketio.SocketIO.start_background_task", _noop).start()
