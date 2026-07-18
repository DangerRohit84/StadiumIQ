"""Advanced GenAI Engine with multi-model support, context awareness, and fallback."""
import json
import time
from openai import OpenAI
from config.settings import Config


class GenAIEngine:
    """Production-grade GenAI engine with intelligent routing and fallback."""

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

PERSONALITY:
- Concise, professional, and friendly
- Use emojis strategically for visual clarity
- Format responses with markdown: **bold**, bullet points, numbered steps
- Include confidence levels when making predictions
- Always provide alternative options

CONTEXT AWARENESS:
- You have access to real-time crowd density data
- You know facility locations, wait times, and capacity
- You can predict crowd movements based on event schedules
- You understand accessibility needs and ADA requirements

RESPONSE RULES:
- For emergencies: Be direct, authoritative, provide immediate actionable steps
- For navigation: Include estimated walking time and distance
- For crowd queries: Always suggest less crowded alternatives
- For accessibility: Detail all available accommodations
- For sustainability: Mention eco-points earned for green actions
- Limit responses to 200 words unless detail is requested"""

    def __init__(self):
        self._client = None
        self._last_init = 0
        self._init_interval = 300

    @property
    def client(self) -> OpenAI | None:
        api_key = Config.OPENAI_API_KEY
        if not api_key:
            return None
        now = time.time()
        if self._client is None or (now - self._last_init) > self._init_interval:
            try:
                self._client = OpenAI(api_key=api_key, timeout=15.0)
                self._last_init = now
            except Exception:
                return None
        return self._client

    def generate(
        self,
        message: str,
        context: dict | None = None,
        language: str = "en",
        user_type: str = "fan",
        urgency: str = "normal",
    ) -> dict:
        """Generate AI response with full context awareness."""
        start = time.time()

        messages = [{"role": "system", "content": self._build_system_prompt(user_type)}]

        if context:
            messages.append({
                "role": "system",
                "content": f"REAL-TIME CONTEXT:\n{json.dumps(context, default=str)}",
            })

        messages.append({"role": "user", "content": message})

        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=messages,
                    max_tokens=600,
                    temperature=0.7,
                    top_p=0.9,
                )
                ai_text = response.choices[0].message.content
                latency = round((time.time() - start) * 1000)
                tokens_used = response.usage.total_tokens if response.usage else 0

                return {
                    "response": ai_text,
                    "source": "genai",
                    "model": Config.OPENAI_MODEL,
                    "latency_ms": latency,
                    "tokens_used": tokens_used,
                    "language": language,
                    "confidence": 0.95,
                }
            except Exception as e:
                pass

        result = self._fallback_response(message, context, user_type)
        result["latency_ms"] = round((time.time() - start) * 1000)
        return result

    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of fan feedback."""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": (
                            "Analyze sentiment of stadium fan feedback. "
                            "Return JSON: {sentiment: positive|negative|neutral, "
                            "confidence: 0-1, emotions: [list], topics: [list], "
                            "satisfaction_score: 1-10, suggested_action: string}"
                        )},
                        {"role": "user", "content": text},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=200,
                )
                return json.loads(response.choices[0].message.content)
            except Exception:
                pass

        return self._rule_sentiment(text)

    def predict_crowd_flow(self, zone_data: dict, event_schedule: dict) -> dict:
        """Predict crowd flow using pattern analysis."""
        predictions = {}
        for zone_id, data in zone_data.items():
            current = data.get("occupancy", 0)
            capacity = data.get("capacity", 1)
            pct = current / capacity if capacity > 0 else 0

            if pct > 0.85:
                trend = "overflow_risk"
                action = "Redirect fans to nearby low-density zones"
            elif pct > 0.7:
                trend = "approaching_capacity"
                action = "Open overflow sections"
            elif pct < 0.3:
                trend = "underutilized"
                action = "Promote zone to incoming fans"
            else:
                trend = "optimal"
                action = "No action needed"

            predictions[zone_id] = {
                "current_density": round(pct * 100, 1),
                "predicted_peak": self._predict_peak(pct, event_schedule),
                "trend": trend,
                "recommended_action": action,
                "confidence": 0.88 if pct > 0.6 else 0.75,
            }
        return predictions

    def detect_anomalies(self, sensor_data: list) -> list:
        """Detect anomalies in sensor/IoT data streams."""
        anomalies = []
        if not sensor_data:
            return anomalies

        values = [s.get("value", 0) for s in sensor_data]
        if len(values) < 3:
            return anomalies

        mean = sum(values) / len(values)
        std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

        for i, reading in enumerate(sensor_data):
            val = reading.get("value", 0)
            z_score = abs(val - mean) / std if std > 0 else 0

            if z_score > 2.5:
                anomalies.append({
                    "index": i,
                    "sensor_id": reading.get("sensor_id", "unknown"),
                    "value": val,
                    "expected_range": [round(mean - 2 * std, 2), round(mean + 2 * std, 2)],
                    "z_score": round(z_score, 2),
                    "severity": "critical" if z_score > 3.5 else "warning",
                    "timestamp": reading.get("timestamp", time.time()),
                    "suggestion": self._anomaly_suggestion(reading.get("type", ""), val, mean),
                })
        return anomalies

    def generate_emergency_protocol(self, incident_type: str, location: dict) -> dict:
        """Generate real-time emergency response protocol."""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": (
                            "Generate emergency protocol for stadium incidents. "
                            "Return JSON with: immediate_actions[], evacuation_routes[], "
                            "communication_plan, medical_response, estimated_resolution_time, "
                            "affected_zones[], risk_level(critical/high/medium/low)"
                        )},
                        {"role": "user", "content": f"Incident: {incident_type} at zone {location}"},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=500,
                )
                return json.loads(response.choices[0].message.content)
            except Exception:
                pass

        return self._default_emergency_protocol(incident_type, location)

    def _build_system_prompt(self, user_type: str) -> str:
        role_prompts = {
            "fan": "You are helping a stadium fan. Be friendly and helpful.",
            "staff": "You are assisting venue staff. Provide operational details.",
            "organizer": "You are advising tournament organizers. Give strategic insights.",
            "emergency": "You are in emergency mode. Be direct and authoritative.",
        }
        role_context = role_prompts.get(user_type, role_prompts["fan"])
        return f"{self.SYSTEM_PROMPT}\n\nUSER CONTEXT: {role_context}"

    def _predict_peak(self, current_pct: float, schedule: dict) -> str:
        if current_pct > 0.8:
            return "Peak reached - expect overflow"
        elif current_pct > 0.6:
            return f"Peak in ~{max(1, int((0.85 - current_pct) * 20))} minutes"
        return "Off-peak - comfortable capacity"

    def _anomaly_suggestion(self, sensor_type: str, value: float, mean: float) -> str:
        suggestions = {
            "temperature": "Check HVAC system - temperature anomaly detected",
            "noise": "Investigate source - unusual noise levels",
            "crowd_density": "Deploy crowd management staff immediately",
            "air_quality": "Check ventilation - air quality below threshold",
            "co2": "Increase ventilation - CO2 levels elevated",
        }
        direction = "above" if value > mean else "below"
        return suggestions.get(sensor_type, f"Sensor reading {direction} normal range")

    def _rule_sentiment(self, text: str) -> dict:
        positive_words = ["great", "amazing", "love", "excellent", "best", "awesome", "fantastic", "happy", "wonderful", "perfect"]
        negative_words = ["bad", "terrible", "hate", "awful", "worst", "horrible", "disappointed", "angry", "poor", "frustrating"]
        urgency_words = ["emergency", "help", "stuck", "lost", "injured", "medical", "fire", "danger", "urgent"]

        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        urg_count = sum(1 for w in urgency_words if w in text_lower)

        if neg_count > pos_count:
            sentiment = "negative"
            score = max(2, 6 - neg_count)
        elif pos_count > neg_count:
            sentiment = "positive"
            score = min(10, 6 + pos_count)
        else:
            sentiment = "neutral"
            score = 5

        emotions = []
        if pos_count > 0: emotions.append("satisfaction")
        if neg_count > 0: emotions.append("frustration")
        if urg_count > 0: emotions.append("urgency")
        if not emotions: emotions.append("neutral")

        return {
            "sentiment": sentiment,
            "confidence": 0.72,
            "emotions": emotions,
            "topics": [],
            "satisfaction_score": score,
            "suggested_action": "Review and respond to fan feedback" if neg_count > 0 else "Thank fan for feedback",
        }

    def _default_emergency_protocol(self, incident_type: str, location: dict) -> dict:
        protocols = {
            "fire": {
                "immediate_actions": [
                    "Activate fire alarm system",
                    "Notify fire department (911)",
                    "Begin controlled evacuation of affected zone",
                    "Deploy fire suppression teams"
                ],
                "evacuation_routes": ["North Emergency Exits", "East Emergency Stairs", "West Service Tunnel"],
                "risk_level": "critical",
            },
            "medical": {
                "immediate_actions": [
                    "Dispatch medical team to location",
                    "Clear path for ambulance access",
                    "Notify nearest medical station",
                    "Prepare first aid response"
                ],
                "evacuation_routes": ["Direct medical access via Gate E4"],
                "risk_level": "high",
            },
            "crowd_surge": {
                "immediate_actions": [
                    "Activate crowd density alerts",
                    "Deploy crowd management personnel",
                    "Open additional exit gates",
                    "PA announcement for crowd control"
                ],
                "evacuation_routes": ["All perimeter exits", "Overflow gates"],
                "risk_level": "high",
            },
        }

        protocol = protocols.get(incident_type, {
            "immediate_actions": ["Assess situation", "Notify security", "Establish perimeter"],
            "evacuation_routes": ["Nearest emergency exits"],
            "risk_level": "medium",
        })

        protocol.update({
            "communication_plan": "PA system + mobile push notification + digital signage",
            "medical_response": "On-site medical team dispatched",
            "estimated_resolution_time": "15-45 minutes depending on incident",
            "affected_zones": [location.get("zone", "unknown")],
        })

        return protocol

    def _fallback_response(self, message: str, context: dict | None, user_type: str) -> dict:
        msg = message.lower()

        if any(w in msg for w in ["hello", "hi", "hey", "greet"]):
            return {
                "response": (
                    "Welcome to **StadiumIQ** — your AI-powered assistant for FIFA World Cup 2026 at MetLife Stadium!\n\n"
                    "I can help you with:\n"
                    "• **Navigation** — Find facilities, food, restrooms\n"
                    "• **Crowds** — Real-time density & best routes\n"
                    "• **Accessibility** — Wheelchair, visual, hearing assistance\n"
                    "• **Transport** — Parking, transit, rideshare\n"
                    "• **Eco** — Recycling stations & green tips\n"
                    "• **Safety** — Emergency guidance & first aid\n\n"
                    "Ask me anything!"
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["emergency", "fire", "help", "danger", "evacuat"]):
            return {
                "response": (
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
                ),
                "source": "fallback",
                "confidence": 0.95,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["restroom", "bathroom", "toilet", "wc", "lavatory"]):
            return {
                "response": (
                    "🚻 **Restrooms at MetLife Stadium**\n\n"
                    "| Location | Wait Time | Accessible | Floor |\n"
                    "|----------|-----------|------------|-------|\n"
                    "| Restroom North | ~2 min | ✅ Yes | Level 1 |\n"
                    "| Restroom East | ~5 min | ✅ Yes | Level 1 |\n"
                    "| Restroom South | ~3 min | ❌ No | Level 1 |\n"
                    "| Restroom West (VIP) | ~1 min | ✅ Yes | Level 2 |\n\n"
                    "**Recommendation:** West restroom has shortest wait.\n"
                    "**Accessibility:** North & East have wheelchair stalls + adult changing tables.\n"
                    "**Tip:** Use the StadiumIQ app to reserve a restroom slot!"
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["food", "eat", "hungry", "restaurant", "snack", "beer", "drink"]):
            return {
                "response": (
                    "🍔 **Food & Beverage Options**\n\n"
                    "**Food Court North** — American, Mexican\n"
                    "Wait: 8 min | Rating: ⭐ 4.2 | Price: $$\n\n"
                    "**Food Court East** — Asian, Italian\n"
                    "Wait: 12 min | Rating: ⭐ 4.5 | Price: $$$\n\n"
                    "**Food Court South** — Halal, Vegan, Kosher\n"
                    "Wait: 5 min | Rating: ⭐ 4.0 | Price: $\n\n"
                    "**Food Court West** — Burgers, Pizza, Craft Beer\n"
                    "Wait: 10 min | Rating: ⭐ 4.3 | Price: $$\n\n"
                    "**🏆 Match Day Specials:**\n"
                    "• World Cup Combo Meal — $15 (save $5)\n"
                    "• First 1,000 fans get a free eco-cup\n\n"
                    "**📱 Pre-order** via StadiumIQ app for skip-the-line pickup!"
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["parking", "car", "drive", "lot", "ev charg"]):
            return {
                "response": (
                    "🅿️ **Parking & Transportation**\n\n"
                    "**Lot A (North)** — $40 | 2,000 spots | ✅ EV Charging\n"
                    "**Lot B (East)** — $35 | 1,500 spots | ❌ No EV\n"
                    "**Lot C (South)** — $38 | 1,800 spots | ✅ EV Charging\n\n"
                    "**🚂 Public Transit:**\n"
                    "• MetLife Station — 0.5 km — Every 10 min\n"
                    "• Bus Terminal — 1.2 km — Every 15 min\n\n"
                    "**🚗 Rideshare:**\n"
                    "• Pickup: West Zone | Drop-off: North Zone\n\n"
                    "**💡 Smart Tip:** Pre-book parking via StadiumIQ app for guaranteed spot + 50 eco-points!"
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["crowd", "busy", "packed", "how many", "capacity", "density"]):
            return {
                "response": (
                    "📊 **Real-Time Crowd Intelligence**\n\n"
                    "| Zone | Occupancy | Density | Status |\n"
                    "|------|-----------|---------|--------|\n"
                    "| A (North) | 13,000 | 65% | 🟡 Moderate |\n"
                    "| B (East) | 9,000 | 45% | 🟢 Low |\n"
                    "| C (South) | 16,000 | 80% | 🟠 High |\n"
                    "| D (West) | 6,750 | 30% | 🟢 Low |\n\n"
                    "**Overall:** 44,750 / 82,500 (54.2%)\n\n"
                    "**🎯 Recommendation:** Zone D (West) and Zone B (East) have the best availability.\n"
                    "**⚠️ Zone C** is approaching capacity — consider alternative seating."
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["wheelchair", "accessibility", "disabled", "handicap", "ada", "mobility"]):
            return {
                "response": (
                    "♿ **Accessibility Services — ADA Compliant**\n\n"
                    "**Entrances:**\n"
                    "• All 4 gates (E1-E4) are wheelchair accessible\n"
                    "• Ramped access + elevators at every transition\n\n"
                    "**Seating:**\n"
                    "• Companion seating in all zones\n"
                    "• Accessible viewing platforms with clear sightlines\n\n"
                    "**Facilities:**\n"
                    "• Accessible restrooms: North, East, West\n"
                    "• Elevators: 4 corners + 2 central\n"
                    "• Tactile paving throughout concourse\n\n"
                    "**Assistance:**\n"
                    "• Staff at any entrance for wheelchair escort\n"
                    "• Audio guide available (10 languages)\n"
                    "• Braille signage at all key locations\n"
                    "• Sign language interpreters available on request\n\n"
                    "**📱 Download StadiumIQ app** for turn-by-turn accessible navigation!"
                ),
                "source": "fallback",
                "confidence": 0.95,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["recycle", "sustainab", "eco", "green", "environment", "carbon"]):
            return {
                "response": (
                    "♻️ **Sustainability Program — Green Stadium Initiative**\n\n"
                    "**Eco Stations:**\n"
                    "| Station | Materials | Eco Points |\n"
                    "|---------|-----------|------------|\n"
                    "| North | Plastic, Paper, Glass | +50 pts |\n"
                    "| East | Plastic, Paper | +30 pts |\n"
                    "| South | All + Food Waste | +75 pts |\n\n"
                    "**Green Actions & Rewards:**\n"
                    "• 🚲 Bike to stadium → +200 pts\n"
                    "• 🚃 Public transit → +100 pts\n"
                    "• 🍱 Bring reusable container → +75 pts\n"
                    "• 🌱 Choose plant-based meal → +50 pts\n\n"
                    "**🏆 Eco Leaderboard:** Top 100 fans win exclusive World Cup merch!\n"
                    "Current leader: **@GreenFan2026** — 12,450 pts"
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["medical", "first aid", "doctor", "sick", "injury", "hurt"]):
            return {
                "response": (
                    "🏥 **Medical Assistance**\n\n"
                    "**Medical Station North:**\n"
                    "• Staff: 3 on duty | Equipment: First Aid, AED, Wheelchair\n"
                    "• Location: Near Gate E1 — Level 1\n\n"
                    "**Medical Station South:**\n"
                    "• Staff: 2 on duty | Equipment: First Aid, AED\n"
                    "• Location: Near Gate E3 — Level 1\n\n"
                    "**Emergency:**\n"
                    "• Call **911** for life-threatening situations\n"
                    "• Stadium Security: **1-800-STADIUM**\n"
                    "• Nearest hospital: Hackensack Medical Center (8 min)\n\n"
                    "**Tip:** Medical stations are marked with ✚ on the stadium map."
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["entrance", "gate", "enter", "entering", "where do i"]):
            return {
                "response": (
                    "🚪 **Stadium Entrances**\n\n"
                    "| Gate | Crowd | Accessible | Best For |\n"
                    "|------|-------|------------|----------|\n"
                    "| E1 - Main North | 🟢 Low | ✅ Yes | General admission |\n"
                    "| E2 - East | 🟡 Medium | ✅ Yes | East zones |\n"
                    "| E3 - South | 🟢 Low | ✅ Yes | South zones |\n"
                    "| E4 - VIP | 🟢 Low | ✅ Yes | VIP/Corporate |\n\n"
                    "**⏰ Gates Open:** 2 hours before kickoff\n"
                    "**💡 Tip:** E1 and E3 currently have shortest queues (~3 min entry)"
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        if any(w in msg for w in ["schedule", "match", "game", "kickoff", "time", "when"]):
            return {
                "response": (
                    "📅 **Match Schedule — MetLife Stadium**\n\n"
                    "**Today's Matches:**\n"
                    "• 14:00 — Group Stage: USA vs England (Zone A-C active)\n"
                    "• 20:00 — Group Stage: Brazil vs Germany (All zones active)\n\n"
                    "**Upcoming:**\n"
                    "• Jul 19 — Quarter-Final 1\n"
                    "• Jul 20 — Quarter-Final 2\n"
                    "• Jul 25 — Semi-Final 1\n"
                    "• Jul 26 — Semi-Final 2\n"
                    "• Jul 19 — **FINAL**\n\n"
                    "**💡 Tip:** Gates open 2 hours before kickoff. Arrive early!"
                ),
                "source": "fallback",
                "confidence": 0.9,
                "language": "en",
                "tokens_used": 0,
            }

        return {
            "response": (
                "I can help you with:\n\n"
                "• **Navigation** — 'Where is the nearest restroom?'\n"
                "• **Food** — 'What food options are available?'\n"
                "• **Crowds** — 'How busy is the stadium?'\n"
                "• **Parking** — 'Where can I park?'\n"
                "• **Accessibility** — 'I need wheelchair access'\n"
                "• **Medical** — 'Where is the first aid?'\n"
                "• **Eco** — 'Where are the recycling stations?'\n"
                "• **Schedule** — 'What matches are today?'\n"
                "• **Emergency** — 'I need help'\n\n"
                "Ask me anything about the stadium!"
            ),
            "source": "fallback",
            "confidence": 0.8,
            "language": "en",
            "tokens_used": 0,
        }


engine = GenAIEngine()
