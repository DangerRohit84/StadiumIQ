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

    LANG_NAMES = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "ar": "Arabic", "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
        "pt": "Portuguese", "hi": "Hindi",
    }

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

        lang_name = self.LANG_NAMES.get(language, "English")
        if language != "en":
            prompt_parts.append(f"IMPORTANT: Respond entirely in {lang_name}. The user's language preference is {lang_name}.")

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

        result = self._fallback_response(message, context, user_type, language)
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

    _TRANSLATIONS = {
        "es": {"hello": "hola", "restroom": "ba\u00f1o", "food": "comida", "parking": "estacionamiento", "crowd": "multitud", "welcome": "Bienvenido a **StadiumIQ** \u2014 tu asistente con IA para la Copa Mundial FIFA 2026 en MetLife Stadium!\n\nPuedo ayudarte con:\n\u2022 **Navegaci\u00f3n** \u2014 Encuentra instalaciones, comida, ba\u00f1os\n\u2022 **Multitudes** \u2014 Densidad en tiempo real y mejores rutas\n\u2022 **Accesibilidad** \u2014 Asistencia para silla de ruedas, visual, auditiva\n\u2022 **Transporte** \u2014 Estacionamiento, tr\u00e1nsito, viajes compartidos\n\u2022 **Eco** \u2014 Estaciones de reciclaje y consejos ecol\u00f3gicos\n\u2022 **Seguridad** \u2014 Gu\u00eda de emergencia y primeros auxilios\n\n\u00a1Preg\u00fabtame lo que quieras!"},
        "fr": {"hello": "bonjour", "restroom": "toilettes", "food": "nourriture", "parking": "parking", "crowd": "foule", "welcome": "Bienvenue sur **StadiumIQ** \u2014 votre assistant IA pour la Coupe du Monde FIFA 2026 au MetLife Stadium!\n\nJe peux vous aider avec:\n\u2022 **Navigation** \u2014 Trouver les installations, la nourriture, les toilettes\n\u2022 **Foules** \u2014 Densit\u00e9 en temps r\u00e9el et meilleures routes\n\u2022 **Accessibilit\u00e9** \u2014 Assistance fauteuil roulant, visuelle, auditive\n\u2022 **Transport** \u2014 Parking, transit, covoiturage\n\u2022 ** \u00c9co** \u2014 Stations de recyclage et conseils \u00e9cologiques\n\nDemandez-moi n\u2019importe quoi!"},
        "de": {"hello": "hallo", "restroom": "Toilette", "food": "Essen", "parking": "Parkplatz", "crowd": "Menge", "welcome": "Willkommen bei **StadiumIQ** \u2014 Ihr KI-Assistent f\u00fcr die FIFA Weltmeisterschaft 2026 im MetLife Stadium!\n\nIch kann Ihnen helfen mit:\n\u2022 **Navigation** \u2014 Einrichtungen, Essen, Toiletten finden\n\u2022 **Mengen** \u2014 Echtzeit-Dichte und beste Routen\n\u2022 **Barrierefreiheit** \u2014 Rollstuhl-, Seh- und H\u00f6rhilfe\n\u2022 **Transport** \u2014 Parkplatz, \u00f6ffentliche Verkehrsmittel\n\nFragen Sie mich was Sie wollen!"},
        "zh": {"hello": "\u4f60\u597d", "restroom": "\u6d17\u624b\u95f4", "food": "\u98df\u7269", "parking": "\u505c\u8f66\u573a", "crowd": "\u4eba\u7fa4", "welcome": "\u6b22\u8fce\u4f7f\u7528 **StadiumIQ** \u2014 \u60a8\u7684FIFA 2026\u4e16\u754c\u676f\u667a\u80fd\u52a9\u624b\uff01\n\n\u6211\u53ef\u4ee5\u5e2e\u52a9\u60a8\uff1a\n\u2022 **\u5bfc\u822a** \u2014 \u67e5\u627e\u8bbe\u65bd\u3001\u98df\u7269\u3001\u6d17\u624b\u95f4\n\u2022 **\u4eba\u7fa4** \u2014 \u5b9e\u65f6\u5bc6\u5ea6\u548c\u6700\u4f73\u8def\u7ebf\n\u2022 **\u65e0\u969c\u788d** \u2014 \u8f6e\u6905\u3001\u89c6\u89c9\u3001\u542c\u89c9\u670d\u52a1\n\n\u95ee\u6211\u4efb\u4f55\u95ee\u9898\uff01"},
        "ja": {"hello": "\u3053\u3093\u306b\u3061\u306f", "restroom": "\u30c8\u30a4\u30ec", "food": "\u98df\u4e8b", "parking": "\u99d0\u8eeb\u5834", "crowd": "\u4eba\u6ce2", "welcome": "**StadiumIQ**\u3078\u3088\u3046\u3053\u305d\uff01FIFA\u30ef\u30fc\u30eb\u30c9\u30ab\u30c3\u30d72026\u306eAI\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8\u3067\u3059\uff01\n\n\u3054\u5229\u7528\u3044\u305f\u3060\u3051\u307e\u3059\uff1a\n\u2022 **\u30ca\u30d3\u30b2\u30fc\u30b7\u30e7\u30f3** \u2014 \u65bd\u8a2d\u3001\u98df\u4e8b\u3001\u30c8\u30a4\u30ec\u63a2\u3057\n\u2022 **\u4eba\u6ce2** \u2014 \u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u5bc6\u5ea6\u3068\u30d9\u30b9\u30c8\u30eb\u30fc\u30c8\n\u2022 **\u30a2\u30af\u30bb\u30b7\u30d3\u30ea\u30c6\u30a3** \u2014 \u30e9\u30f3\u30d7\u30b7\u30e3\u30fc\u30eb\u3001\u898b\u3048\u3001\u805a\u97f3\u670d\u52a1\n\n\u4f55\u3067\u3082\u304a\u554f\u3044\u5408\u308f\u305b\u304f\u3060\u3055\u3044\uff01"},
        "ko": {"hello": "\uc548\ub155\ud558\uc138\uc694", "restroom": "\uc708\ub300\uc2dc\uacfc", "food": "\uc2f8\ubc00", "parking": "\uc8fc\ucc28\uc7a5", "crowd": "\uc778\ud0a4", "welcome": "**StadiumIQ**\ub85c \uc624\uc2e0 \uac83\uc744 \ud658\uc601\ud569\ub2c8\ub2e4! FIFA \uc6d4\ub4dc\ucee8\ud504 2026 AI \uc2dc\uc2a4\ud15c \uc390\uc2a4\ud2b8\ub2e4.\n\n\ub3c4\uc6c0\ub9cc \ubc14\ub824 \ub4dc\ub9bd\ub2c8\ub2e4:\n\u2022 **\ub124\uc774\ubc84\uc774\uc158** \u2014 \uc2dc\uc124, \uc2f8\ubc00, \uc708\ub300\uc2dc\uacfc \ucc3e\uae30\n\u2022 **\uc778\ud0a4** \u2014 \uc2e4\uc2dc\uac04 \ubc00\ub3c4\uc640 \ucd5c\uc801 \uacbd\ub85c\n\u2022 **\ubb34\uc5e7\ud558\uc9c0 \uc5c6\uc774** \u2014 \ubc00\ud0a4\ucc7c, \uc2dc\uacfc, \uccad\uc5b4 \ub3c4\uc6c0\n\n\ubb34\uc5c0\uc774\ub4e0 \ubb3c\uc5b4\ubcf4\uc138\uc694!"},
        "pt": {"hello": "ol\u00e1", "restroom": "banheiro", "food": "comida", "parking": "estacionamento", "crowd": "multid\u00e3o", "welcome": "Bem-vindo ao **StadiumIQ** \u2014 seu assistente de IA para a Copa do Mundo FIFA 2026 no MetLife Stadium!\n\nPosso ajudar com:\n\u2022 **Navega\u00e7\u00e3o** \u2014 Encontrar instala\u00e7\u00f5es, comida, banheiros\n\u2022 **Multid\u00e3o** \u2014 Densidade em tempo real e melhores rotas\n\u2022 **Acessibilidade** \u2014 Cadeira de rodas, visual, auditiva\n\nPergunte qualquer coisa!"},
        "hi": {"hello": "\u0928\u092e\u0938\u094d\u0924\u0947", "restroom": "\u0936\u094c\u091a\u093e\u0918\u0930", "food": "\u0916\u093e\u0928\u093e", "parking": "\u092a\u093e\u0930\u094d\u0915\u093f\u0902\u0917", "crowd": "\u092d\u0940\u0921\u093c", "welcome": "**StadiumIQ** \u092e\u0947\u0902 \u0906\u092a\u0915\u093e \u0938\u094d\u0935\u093e\u0917\u0924 \u0939\u0948! FIFA \u0935\u0930\u094d\u0932\u094d\u0921 \u0915\u092a 2026 \u0915\u0947 \u0932\u093f\u090f AI \u0938\u0939\u093e\u092f\u0915!\n\n\u092e\u0948\u0902 \u0906\u092a\u0915\u0940 \u092e\u0926\u0926 \u0915\u0930 \u0938\u0915\u0924\u093e \u0939\u0942\u0902:\n\u2022 **\u0928\u0947\u0935\u093f\u0917\u0947\u0936\u0928** \u2014 \u0938\u0941\u0935\u093f\u0927\u093e\u090f\u0901, \u0916\u093e\u0928\u093e, \u0936\u094c\u091a\u093e\u0918\u0930\n\u2022 **\u092d\u0940\u0921\u093c** \u2014 \u0930\u093f\u092f\u0932 \u091f\u093e\u0907\u092e \u0921\u0947\u0902\u0938\u093f\u091f\u0940\n\n\u0915\u0941\u0924\u0940 \u092d\u0940 \u092a\u0942\u091b\u0947\u0902!"},
    }

    def _fallback_response(self, message: str, context: dict | None, user_type: str, language: str = "en") -> dict:
        msg = message.lower()

        # If non-English, try to find a translated response
        if language != "en" and language in self._TRANSLATIONS:
            trans = self._TRANSLATIONS[language]
            if "hello" in msg or any(w in msg for w in ["hi", "hey"]):
                return {"response": trans.get("welcome", "Welcome to **StadiumIQ**!"), "source": "fallback", "confidence": 0.9, "language": language, "tokens_used": 0}

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
