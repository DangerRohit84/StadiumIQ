"""Sentiment Analysis Engine for fan feedback."""
import logging
import re
import time
from core.database import db

logger = logging.getLogger(__name__)

MAX_FEEDBACK_LOG = 1000


class SentimentAnalyzer:
    """Analyzes fan sentiment from multiple sources."""

    POSITIVE_WORDS = frozenset([
        "great", "amazing", "love", "excellent", "best", "awesome", "fantastic",
        "happy", "wonderful", "perfect", "incredible", "outstanding", "brilliant",
        "enjoy", "fun", "exciting", "thrilling", "impressive", "recommend",
    ])

    NEGATIVE_WORDS = frozenset([
        "bad", "terrible", "hate", "awful", "worst", "horrible", "disappointed",
        "angry", "poor", "frustrating", "annoying", "slow", "dirty", "crowded",
        "expensive", "rude", "broken", "unfair", "unsafe", "uncomfortable",
    ])

    URGENCY_WORDS = frozenset([
        "emergency", "help", "stuck", "lost", "injured", "medical", "fire",
        "danger", "urgent", "trapped", "panic", "evacuate",
    ])

    TOPIC_KEYWORDS = {
        "navigation": ["find", "where", "direction", "locate", "map", "gate", "entrance"],
        "food": ["food", "eat", "hungry", "restaurant", "snack", "drink", "beer", "menu"],
        "crowd": ["crowd", "busy", "packed", "line", "queue", "wait", "full"],
        "accessibility": ["wheelchair", "disabled", "accessibility", "ada", "mobility", "ramp", "elevator"],
        "safety": ["safe", "security", "emergency", "danger", "threat", "suspicious"],
        "transport": ["parking", "car", "transit", "bus", "train", "rideshare", "uber"],
        "sustainability": ["recycle", "eco", "green", "sustainable", "environment", "carbon"],
        "facility": ["restroom", "bathroom", "seat", "wifi", "screen", "shop"],
    }

    _POS_PATTERNS: dict[str, re.Pattern] = {}
    _NEG_PATTERNS: dict[str, re.Pattern] = {}
    _URG_PATTERNS: dict[str, re.Pattern] = {}
    _TOPIC_PATTERNS: dict[str, list[re.Pattern]] = {}
    _patterns_built = False

    @classmethod
    def _build_patterns(cls) -> None:
        """Compile regex patterns for positive, negative, urgency, and topic keywords."""
        if cls._patterns_built:
            return
        for w in cls.POSITIVE_WORDS:
            cls._POS_PATTERNS[w] = re.compile(r'\b' + re.escape(w) + r'\b')
        for w in cls.NEGATIVE_WORDS:
            cls._NEG_PATTERNS[w] = re.compile(r'\b' + re.escape(w) + r'\b')
        for w in cls.URGENCY_WORDS:
            cls._URG_PATTERNS[w] = re.compile(r'\b' + re.escape(w) + r'\b')
        for topic, keywords in cls.TOPIC_KEYWORDS.items():
            cls._TOPIC_PATTERNS[topic] = [re.compile(r'\b' + re.escape(kw) + r'\b') for kw in keywords]
        cls._patterns_built = True

    def __init__(self) -> None:
        """Initialize the sentiment analyzer."""
        self._build_patterns()
        self.feedback_log: list[dict] = []
        self._sentiment_trend: list[dict] = []

    def analyze(self, text: str, source: str = "chat") -> dict:
        """Analyze sentiment of a single piece of feedback.

        Tries Gemini first for higher accuracy, falls back to rule-based.
        """
        result = None
        try:
            from core.ai.genai_engine import engine
            if engine.is_available():
                gemini_result = engine.analyze_sentiment(text)
                if gemini_result and "sentiment" in gemini_result:
                    result = gemini_result
        except Exception:
            pass

        if result is None:
            result = self._rule_based_analysis(text)

        result["source"] = source
        result["timestamp"] = time.time()

        self.feedback_log.append(result)
        if len(self.feedback_log) > MAX_FEEDBACK_LOG:
            self.feedback_log = self.feedback_log[-MAX_FEEDBACK_LOG:]

        try:
            db.save_sentiment(text, result["sentiment"], result["satisfaction_score"])
        except Exception:
            pass

        self._sentiment_trend.append({
            "time": time.time(),
            "score": result["satisfaction_score"],
        })

        if len(self._sentiment_trend) > 200:
            self._sentiment_trend = self._sentiment_trend[-200:]

        return result

    def get_feedback_summary(self, last_n: int = 50) -> dict:
        """Get aggregated sentiment summary."""
        recent = self.feedback_log[-last_n:] if self.feedback_log else []
        if not recent:
            return {
                "total_feedback": 0,
                "average_score": 5,
                "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                "top_topics": [],
                "trend": "stable",
            }

        scores = [f["satisfaction_score"] for f in recent]
        sentiments = [f["sentiment"] for f in recent]

        topic_counts = {}
        for f in recent:
            for topic in f.get("topics", []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        trend = "stable"
        if len(self._sentiment_trend) >= 10:
            recent_scores = [t["score"] for t in self._sentiment_trend[-10:]]
            older_scores = [t["score"] for t in self._sentiment_trend[-20:-10]]
            if older_scores:
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores)
                if recent_avg > older_avg + 0.5:
                    trend = "improving"
                elif recent_avg < older_avg - 0.5:
                    trend = "declining"

        return {
            "total_feedback": len(self.feedback_log),
            "average_score": round(sum(scores) / len(scores), 1),
            "sentiment_distribution": {
                "positive": sentiments.count("positive"),
                "negative": sentiments.count("negative"),
                "neutral": sentiments.count("neutral"),
            },
            "top_topics": sorted(topic_counts.items(), key=lambda x: -x[1])[:5],
            "trend": trend,
        }

    def get_sentiment_chart_data(self) -> list[dict]:
        """Get time-series data for sentiment chart."""
        return [
            {"time": t["time"], "score": t["score"]}
            for t in self._sentiment_trend[-50:]
        ]

    def _rule_based_analysis(self, text: str) -> dict:
        """Rule-based sentiment analysis with word boundary matching."""
        text_lower = text.lower()

        pos_count = sum(1 for pat in self._POS_PATTERNS.values() if pat.search(text_lower))
        neg_count = sum(1 for pat in self._NEG_PATTERNS.values() if pat.search(text_lower))
        urg_count = sum(1 for pat in self._URG_PATTERNS.values() if pat.search(text_lower))

        topics: list[str] = []
        for topic, patterns in self._TOPIC_PATTERNS.items():
            if any(pat.search(text_lower) for pat in patterns):
                topics.append(topic)

        if neg_count > pos_count:
            sentiment = "negative"
            score = max(1, 5 - neg_count)
        elif pos_count > neg_count:
            sentiment = "positive"
            score = min(10, 5 + pos_count)
        else:
            sentiment = "neutral"
            score = 5

        emotions: list[str] = []
        if pos_count > 0: emotions.append("satisfaction")
        if neg_count > 0: emotions.append("frustration")
        if urg_count > 0: emotions.append("urgency")
        if "!" in text: emotions.append("excitement" if pos_count > neg_count else "anger")
        if not emotions: emotions.append("neutral")

        suggested_action = "No action needed"
        if neg_count > 2:
            suggested_action = "Escalate to customer service team"
        elif neg_count > 0:
            suggested_action = "Send follow-up to address concerns"
        elif urg_count > 0:
            suggested_action = "Priority response required"

        return {
            "sentiment": sentiment,
            "confidence": min(0.95, 0.6 + (pos_count + neg_count) * 0.05),
            "emotions": emotions,
            "topics": topics,
            "satisfaction_score": score,
            "suggested_action": suggested_action,
            "keywords_found": {
                "positive": [w for w, pat in self._POS_PATTERNS.items() if pat.search(text_lower)],
                "negative": [w for w, pat in self._NEG_PATTERNS.items() if pat.search(text_lower)],
                "urgency": [w for w, pat in self._URG_PATTERNS.items() if pat.search(text_lower)],
            },
        }


sentiment_analyzer = SentimentAnalyzer()
