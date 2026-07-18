"""Sentiment Analysis Engine for fan feedback."""
import time
from typing import Any


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

    def __init__(self):
        self.feedback_log = []
        self._sentiment_trend = []

    def analyze(self, text: str, source: str = "chat") -> dict:
        """Analyze sentiment of a single piece of feedback."""
        result = self._rule_based_analysis(text)
        result["source"] = source
        result["timestamp"] = time.time()

        self.feedback_log.append(result)
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

    def get_sentiment_chart_data(self) -> list:
        """Get time-series data for sentiment chart."""
        return [
            {"time": t["time"], "score": t["score"]}
            for t in self._sentiment_trend[-50:]
        ]

    def _rule_based_analysis(self, text: str) -> dict:
        text_lower = text.lower()
        words = text_lower.split()

        pos_count = sum(1 for w in self.POSITIVE_WORDS if w in text_lower)
        neg_count = sum(1 for w in self.NEGATIVE_WORDS if w in text_lower)
        urg_count = sum(1 for w in self.URGENCY_WORDS if w in text_lower)

        topics = []
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
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

        emotions = []
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
                "positive": [w for w in self.POSITIVE_WORDS if w in text_lower],
                "negative": [w for w in self.NEGATIVE_WORDS if w in text_lower],
                "urgency": [w for w in self.URGENCY_WORDS if w in text_lower],
            },
        }


sentiment_analyzer = SentimentAnalyzer()
