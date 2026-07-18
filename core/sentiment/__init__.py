"""Sentiment analysis subsystem for fan feedback processing.

Exposes the SentimentAnalyzer singleton that classifies fan text
into positive/negative/neutral sentiments with urgency detection.
"""
from core.sentiment.sentiment_engine import sentiment_analyzer

__all__ = ["sentiment_analyzer"]
