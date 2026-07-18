"""GenAI Engine powered by Google Gemini 2.5 Flash with intelligent fallback."""
import json
import time
import google.generativeai as genai
from config.settings import Config


class GenAIEngine:
    """Production-grade GenAI engine using Google Gemini 2.5 Flash."""

    SYSTEM_PROMPT = """You are StadiumIQ Brain — a state-of-the-art AI assistant for FIFA World Cup 2026 at MetLife Stadium.

CAPABILITIES:
1. Real-time crowd intelligence and predictive analytics
2. Emergency evacuation guidance and safety protocols
3. Multilingual fan assistance (10 languages)
4. Accessibility-first navigation for disabled fans
5. Sustainability and eco-points guidance
6. Sentiment analysis of fan feedback
7. Operational intelligence for venue staff
8. Transportation optimization and parking guidance
9. Live match simulation and predictions
10. Personalized fan journey assistance

PERSONALITY:
- Concise, professional, and friendly
- Use emojis strategically for visual clarity
- Format responses with markdown: **bold**, bullet points, numbered steps
- Include confidence levels when making predictions
- Always provide alternative options
- Remember context from earlier in the conversation

RESPONSE RULES:
- For emergencies: Be direct, authoritative, provide immediate actionable steps
- For navigation: Include estimated walking time and distance
- For crowd queries: Always suggest less crowded alternatives
- For accessibility: Detail all available accommodations
- For sustainability: Mention eco-points earned for green actions
- Limit responses to 200 words unless detail is requested"""

    def __init__(self):
        self._model = None
        self._conversation_history = {}
        self._configure_gemini()

    def _configure_gemini(self):
        """Configure Google Gemini API."""
        api_key = Config.GOOGLE_API_KEY
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(
                    Config.GOOGLE_MODEL,
                    system_instruction=self.SYSTEM_PROMPT,
                )
            except Exception:
                self._model = None

    def generate(
        self,
        message: str,
        context: dict | None = None,
        language: str = "en",
        user_type: str = "fan",
        urgency: str = "normal",
        fan_id: str | None = None,
    ) -> dict:
        """Generate AI response using Gemini 2.5 Flash with multi-turn memory."""
        start = time.time()

        prompt_parts = []

        # Add conversation history for multi-turn context
        if fan_id and fan_id in self._conversation_history:
            history = self._conversation_history[fan_id][-6:]
            for msg in history:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt_parts.append(f"{role}: {msg['content']}")

        if context:
            prompt_parts.append(f"REAL-TIME CONTEXT:\n{json.dumps(context, default=str)}")

        prompt_parts.append(f"USER: {message}")
        full_prompt = "\n\n".join(prompt_parts)

        if self._model:
            try:
                response = self._model.generate_content(full_prompt)
                ai_text = response.text
                latency = round((time.time() - start) * 1000)
                tokens_used = 0
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    tokens_used = getattr(response.usage_metadata, 'total_token_count', 0)

                # Save conversation history
                if fan_id:
                    if fan_id not in self._conversation_history:
                        self._conversation_history[fan_id] = []
                    self._conversation_history[fan_id].append({"role": "user", "content": message})
                    self._conversation_history[fan_id].append({"role": "assistant", "content": ai_text})
                    if len(self._conversation_history[fan_id]) > 20:
                        self._conversation_history[fan_id] = self._conversation_history[fan_id][-20:]

                return {
                    "response": ai_text,
                    "source": "gemini-2.5-flash",
                    "model": Config.GOOGLE_MODEL,
                    "latency_ms": latency,
                    "tokens_used": tokens_used,
                    "language": language,
                    "confidence": 0.95,
                }
            except Exception:
                pass

        result = self._fallback_response(message, context, user_type)
        result["latency_ms"] = round((time.time() - start) * 1000)

        # Save conversation history even for fallback
        if fan_id:
            if fan_id not in self._conversation_history:
                self._conversation_history[fan_id] = []
            self._conversation_history[fan_id].append({"role": "user", "content": message})
            self._conversation_history[fan_id].append({"role": "assistant", "content": result["response"]})
            if len(self._conversation_history[fan_id]) > 20:
                self._conversation_history[fan_id] = self._conversation_history[fan_id][-20:]

        return result

    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using Gemini."""
        if self._model:
            try:
                response = self._model.generate_content(
                    f"Analyze sentiment of this stadium fan feedback. "
                    f"Return ONLY valid JSON (no markdown): "
                    f'{{"sentiment": "positive|negative|neutral", "confidence": 0-1, '
                    f'"emotions": ["list"], "topics": ["list"], '
                    f'"satisfaction_score": 1-10, "suggested_action": "string"}}\n\n'
                    f"Feedback: {text}"
                )
                raw = response.text.strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                return json.loads(raw)
            except Exception:
                pass
        return self._rule_sentiment(text)

    def _rule_sentiment(self, text: str) -> dict:
        positive_words = ["great", "amazing", "love", "excellent", "best", "awesome", "fantastic", "happy", "wonderful", "perfect"]
        negative_words = ["bad", "terrible", "hate", "awful", "worst", "horrible", "disappointed", "angry", "poor", "frustrating"]
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if neg_count > pos_count:
            sentiment, score = "negative", max(2, 6 - neg_count)
        elif pos_count > neg_count:
            sentiment, score = "positive", min(10, 6 + pos_count)
        else:
            sentiment, score = "neutral", 5

        return {"sentiment": sentiment, "confidence": 0.72, "emotions": [], "topics": [],
                "satisfaction_score": score, "suggested_action": "Review feedback"}

    def _fallback_response(self, message: str, context: dict | None, user_type: str) -> dict:
        msg = message.lower()

        if any(w in msg for w in ["hello", "hi", "hey", "greet"]):
            return {"response": (
                "Welcome to **StadiumIQ** — your AI-powered assistant for FIFA World Cup 2026 at MetLife Stadium!\n\n"
                "I can help you with:\n"
                "• **Navigation** — Find facilities, food, restrooms\n"
                "• **Crowds** — Real-time density & best routes\n"
                "• **Accessibility** — Wheelchair, visual, hearing assistance\n"
                "• **Transport** — Parking, transit, rideshare\n"
                "• **Eco** — Recycling stations & green tips\n"
                "• **Safety** — Emergency guidance & first aid\n"
                "• **Match** — Live scores, predictions, energy\n\n"
                "Ask me anything!"
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["emergency", "fire", "help", "danger", "evacuat"]):
            return {"response": (
                "🚨 **EMERGENCY PROTOCOL ACTIVATED**\n\n"
                "**Immediate Steps:**\n"
                "1. Stay calm and follow staff instructions\n"
                "2. Move toward the nearest marked emergency exit\n"
                "3. Do NOT use elevators — use stairs only\n"
                "4. If injured, call **911** immediately\n\n"
                "**Emergency Exits:** North (E1), South (E3), East (E2)\n"
                "**Medical Stations:** North & South concourse\n"
                "**Security Hotline:** 1-800-STADIUM\n\n"
                "Evacuation routes are shown on digital signage throughout the stadium."
            ), "source": "fallback", "confidence": 0.95, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["restroom", "bathroom", "toilet", "wc"]):
            return {"response": (
                "🚻 **Restrooms at MetLife Stadium**\n\n"
                "| Location | Wait | Accessible |\n"
                "|----------|------|------------|\n"
                "| North | ~2 min | ✅ Yes |\n"
                "| East | ~5 min | ✅ Yes |\n"
                "| South | ~3 min | ❌ No |\n"
                "| West (VIP) | ~1 min | ✅ Yes |\n\n"
                "**Tip:** West restroom has shortest wait!"
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["food", "eat", "hungry", "restaurant", "snack", "beer"]):
            return {"response": (
                "🍔 **Food & Beverage Options**\n\n"
                "**North** — American, Mexican | Wait: 8 min | ⭐ 4.2\n"
                "**East** — Asian, Italian | Wait: 12 min | ⭐ 4.5\n"
                "**South** — Halal, Vegan, Kosher | Wait: 5 min | ⭐ 4.0\n"
                "**West** — Burgers, Pizza, Craft Beer | Wait: 10 min | ⭐ 4.3\n\n"
                "**📱 Pre-order** via StadiumIQ app for skip-the-line pickup!"
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["parking", "car", "drive", "lot"]):
            return {"response": (
                "🅿️ **Parking & Transportation**\n\n"
                "**Lot A (North)** — $40 | 2,000 spots | ✅ EV Charging\n"
                "**Lot B (East)** — $35 | 1,500 spots | ❌ No EV\n"
                "**Lot C (South)** — $38 | 1,800 spots | ✅ EV Charging\n\n"
                "**🚂 Public Transit:** MetLife Station 0.5 km — Every 10 min\n"
                "**🚗 Rideshare:** Pickup: West | Drop-off: North\n\n"
                "**💡 Pre-book parking** for guaranteed spot + 50 eco-points!"
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["crowd", "busy", "packed", "how many", "density"]):
            return {"response": (
                "📊 **Real-Time Crowd Intelligence**\n\n"
                "| Zone | Occupancy | Status |\n"
                "|------|-----------|--------|\n"
                "| A (North) | 65% | 🟡 Moderate |\n"
                "| B (East) | 45% | 🟢 Low |\n"
                "| C (South) | 80% | 🟠 High |\n"
                "| D (West) | 30% | 🟢 Low |\n\n"
                "**🎯 Best availability:** Zone D & Zone B\n"
                "**⚠️ Zone C** approaching capacity"
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["wheelchair", "accessibility", "disabled", "ada", "mobility"]):
            return {"response": (
                "♿ **Accessibility Services — ADA Compliant**\n\n"
                "• All 4 gates wheelchair accessible with ramps + elevators\n"
                "• Companion seating in all zones\n"
                "• Accessible restrooms: North, East, West\n"
                "• Tactile paving throughout concourse\n"
                "• Audio guide in 10 languages\n"
                "• Sign language interpreters on request\n\n"
                "**📱 Download StadiumIQ app** for turn-by-turn accessible navigation!"
            ), "source": "fallback", "confidence": 0.95, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["recycle", "sustainab", "eco", "green"]):
            return {"response": (
                "♻️ **Sustainability Program**\n\n"
                "| Station | Materials | Points |\n"
                "|---------|-----------|--------|\n"
                "| North | Plastic, Paper, Glass | +50 |\n"
                "| East | Plastic, Paper | +30 |\n"
                "| South | All + Food Waste | +75 |\n\n"
                "**Green Actions:**\n"
                "• 🚲 Bike → +200 pts | 🚃 Transit → +100 pts\n"
                "• 🍱 Reusable container → +75 pts | 🌱 Plant-based → +50 pts"
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["medical", "first aid", "doctor", "sick", "injury"]):
            return {"response": (
                "🏥 **Medical Assistance**\n\n"
                "**Station North:** 3 staff | First Aid, AED, Wheelchair\n"
                "**Station South:** 2 staff | First Aid, AED\n\n"
                "**Emergency:** Call **911**\n"
                "**Stadium Security:** 1-800-STADIUM\n"
                "**Nearest Hospital:** Hackensack Medical (8 min)\n\n"
                "Medical stations marked with ✚ on the map."
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["schedule", "match", "game", "kickoff", "when"]):
            return {"response": (
                "📅 **Match Schedule — MetLife Stadium**\n\n"
                "**Today:**\n"
                "• 14:00 — USA vs England (Group Stage)\n"
                "• 20:00 — Brazil vs Germany (Group Stage)\n\n"
                "**Upcoming:**\n"
                "• Jul 19-20 — Quarter-Finals\n"
                "• Jul 25-26 — Semi-Finals\n"
                "• Jul 19 — **FINAL**\n\n"
                "Gates open 2 hours before kickoff!"
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        if any(w in msg for w in ["match score", "live score", "score", "who winning"]):
            return {"response": (
                "⚽ **Live Match**\n\n"
                "Start a match simulation to see live scores!\n\n"
                "Use: `POST /api/match/simulate`\n"
                "Or ask me to simulate a match between any two teams.\n\n"
                "**Available teams:** USA, ENG, BRA, GER, FRA, ARG, ESP, JPN"
            ), "source": "fallback", "confidence": 0.9, "language": "en", "tokens_used": 0}

        return {"response": (
            "I can help you with:\n\n"
            "• **Navigation** — 'Where is the nearest restroom?'\n"
            "• **Food** — 'What food options are available?'\n"
            "• **Crowds** — 'How busy is the stadium?'\n"
            "• **Parking** — 'Where can I park?'\n"
            "• **Accessibility** — 'I need wheelchair access'\n"
            "• **Medical** — 'Where is the first aid?'\n"
            "• **Eco** — 'Where are the recycling stations?'\n"
            "• **Schedule** — 'What matches are today?'\n"
            "• **Match** — 'Simulate USA vs Brazil'\n\n"
            "Ask me anything about the stadium!"
        ), "source": "fallback", "confidence": 0.8, "language": "en", "tokens_used": 0}


engine = GenAIEngine()
