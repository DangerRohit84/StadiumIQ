"""AI subsystem for natural language processing and generative responses.

Exposes the GenAIEngine singleton that powers multilingual fan
assistance, operational intelligence queries, and real-time chat.
"""
from core.ai.genai_engine import engine

__all__ = ["engine"]
