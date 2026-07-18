"""AI Match Simulator — live match events, score predictions, and momentum analysis."""
import random
import time
from typing import Any


class MatchSimulator:
    """Simulates live match events and provides AI-powered analysis."""

    TEAMS = {
        "USA": {"rating": 82, "form": [1, 0, 1, 1, 0], "style": "counter-attack"},
        "ENG": {"rating": 85, "form": [1, 1, 1, 0, 1], "style": "possession"},
        "BRA": {"rating": 88, "form": [1, 1, 1, 1, 0], "style": "technical"},
        "GER": {"rating": 84, "form": [0, 1, 1, 1, 1], "style": "organized"},
        "FRA": {"rating": 87, "form": [1, 1, 0, 1, 1], "style": "dynamic"},
        "ARG": {"rating": 86, "form": [1, 0, 1, 1, 1], "style": "creative"},
        "ESP": {"rating": 86, "form": [1, 1, 1, 1, 0], "style": "tiki-taka"},
        "JPN": {"rating": 78, "form": [1, 1, 0, 1, 1], "style": "high-press"},
    }

    MATCH_EVENTS = {
        "goal": {"weight": 15, "excitement": 10},
        "shot_on_target": {"weight": 25, "excitement": 6},
        "shot_off_target": {"weight": 20, "excitement": 3},
        "foul": {"weight": 30, "excitement": 2},
        "corner": {"weight": 20, "excitement": 4},
        "free_kick": {"weight": 15, "excitement": 5},
        "yellow_card": {"weight": 8, "excitement": 7},
        "red_card": {"weight": 2, "excitement": 10},
        "penalty": {"weight": 3, "excitement": 10},
        "substitution": {"weight": 12, "excitement": 3},
        "offside": {"weight": 10, "excitement": 1},
        "save": {"weight": 18, "excitement": 5},
    }

    COMMENTARY = {
        "goal": [
            "GOAL! What a fantastic finish! The crowd erupts!",
            "GOAL! Unbelievable strike! MetLife Stadium is rocking!",
            "GOAL! Top corner! The keeper had no chance!",
        ],
        "shot_on_target": [
            "Shot on target! Good save by the keeper.",
            "Powerful effort! The keeper pushes it wide.",
            "On target! Just over the bar!",
        ],
        "foul": [
            "Foul committed. Free kick awarded.",
            "That's a late challenge. Referee reaches for the whistle.",
            "Foul in a dangerous position.",
        ],
        "corner": [
            "Corner kick. Good opportunity here.",
            "Corner awarded. The tall players move forward.",
        ],
        "yellow_card": [
            "Yellow card shown. The player needs to be careful.",
            "Booking! That's a yellow card.",
        ],
        "red_card": [
            "RED CARD! He's been sent off! Down to 10 men!",
        ],
        "penalty": [
            "PENALTY! The referee points to the spot!",
        ],
        "substitution": [
            "Substitution made. Fresh legs on the pitch.",
            "Tactical change. The manager reshuffles.",
        ],
        "save": [
            "Great save! The keeper denies the attacker.",
            "What a stop! Reaction save at its finest.",
        ],
    }

    def __init__(self):
        self.active_match = None
        self.event_log = []
        self.momentum = {"home": 50, "away": 50}

    def start_match(self, home_team: str, away_team: str) -> dict:
        """Start a new match simulation."""
        self.active_match = {
            "id": f"MATCH-{int(time.time())}",
            "home": home_team,
            "away": away_team,
            "home_score": 0,
            "away_score": 0,
            "minute": 0,
            "status": "live",
            "half": 1,
            "home_stats": {"possession": 50, "shots": 0, "shots_on_target": 0, "fouls": 0, "corners": 0, "cards": 0},
            "away_stats": {"possession": 50, "shots": 0, "shots_on_target": 0, "fouls": 0, "corners": 0, "cards": 0},
            "started_at": time.time(),
        }
        self.event_log = []
        self.momentum = {"home": 50, "away": 50}
        return self.get_match_status()

    def simulate_minute(self) -> dict:
        """Simulate one minute of match action."""
        if not self.active_match or self.active_match["status"] != "live":
            return {"error": "No active match"}

        self.active_match["minute"] += 1
        minute = self.active_match["minute"]

        if minute == 45:
            self.active_match["half"] = 2
        elif minute >= 90:
            self.active_match["status"] = "finished"
            return self.get_match_status()

        event = self._generate_event()
        if event:
            self._process_event(event)

        self._update_momentum()
        self._update_possession()

        return self.get_match_status()

    def simulate_full_match(self, home_team: str, away_team: str) -> dict:
        """Simulate an entire match instantly."""
        self.start_match(home_team, away_team)
        while self.active_match["status"] == "live":
            self.simulate_minute()
        return self.get_match_status()

    def get_match_status(self) -> dict:
        """Get current match status."""
        if not self.active_match:
            return {"error": "No active match"}
        return {**self.active_match, "momentum": dict(self.momentum)}

    def get_recent_events(self, count: int = 5) -> list:
        """Get recent match events."""
        return self.event_log[-count:]

    def get_prediction(self) -> dict:
        """AI-powered match prediction based on current state."""
        if not self.active_match:
            return {"error": "No active match"}

        home = self.active_match["home"]
        away = self.active_match["away"]
        home_score = self.active_match["home_score"]
        away_score = self.active_match["away_score"]
        minute = self.active_match["minute"]

        home_strength = self.TEAMS.get(home, {}).get("rating", 80)
        away_strength = self.TEAMS.get(away, {}).get("rating", 80)

        home_momentum_boost = (self.momentum["home"] - 50) * 0.1
        score_diff = home_score - away_score

        remaining = max(1, 90 - minute)

        home_win_prob = min(95, max(5, 40 + (home_strength - away_strength) + home_momentum_boost + score_diff * 15))
        draw_prob = min(40, max(5, 25 - abs(score_diff) * 10 - abs(home_strength - away_strength) * 0.5))
        away_win_prob = max(5, 100 - home_win_prob - draw_prob)

        if minute < 30:
            confidence = 0.55
        elif minute < 60:
            confidence = 0.72
        elif minute < 75:
            confidence = 0.85
        else:
            confidence = 0.93

        next_event = self._predict_next_event()

        return {
            "home_win_probability": round(home_win_prob, 1),
            "draw_probability": round(draw_prob, 1),
            "away_win_probability": round(away_win_prob, 1),
            "predicted_final_score": f"{home_score + (1 if home_win_prob > 50 else 0)}-{away_score + (1 if away_win_prob > 40 else 0)}",
            "confidence": round(confidence, 2),
            "next_event_prediction": next_event,
            "momentum_shift": "home" if self.momentum["home"] > 60 else "away" if self.momentum["away"] > 60 else "balanced",
        }

    def get_crowd_energy(self) -> dict:
        """Calculate crowd energy based on match events."""
        recent = self.event_log[-10:]
        energy = 50

        for event in recent:
            event_type = event.get("type", "")
            if event_type == "goal":
                energy += 30
            elif event_type in ("shot_on_target", "save"):
                energy += 10
            elif event_type == "penalty":
                energy += 25
            elif event_type == "red_card":
                energy += 15

        energy = min(100, max(0, energy))

        if energy > 80:
            level = "electric"
        elif energy > 60:
            level = "excited"
        elif energy > 40:
            level = "engaged"
        elif energy > 20:
            level = "calm"
        else:
            level = "quiet"

        return {
            "energy_level": energy,
            "level_name": level,
            "description": self._energy_description(level),
        }

    def _generate_event(self) -> dict | None:
        minute = self.active_match["minute"]
        home = self.active_match["home"]
        away = self.active_match["away"]

        if random.random() > 0.35:
            return None

        event_type = random.choices(
            list(self.MATCH_EVENTS.keys()),
            weights=[e["weight"] for e in self.MATCH_EVENTS.values()]
        )[0]

        team = "home" if random.random() < 0.55 else "away"
        team_name = home if team == "home" else away

        commentary_list = self.COMMENTARY.get(event_type, ["Event occurred."])
        commentary = random.choice(commentary_list)

        return {
            "type": event_type,
            "team": team,
            "team_name": team_name,
            "minute": minute,
            "commentary": commentary,
            "excitement": self.MATCH_EVENTS[event_type]["excitement"],
        }

    def _process_event(self, event: dict):
        self.event_log.append(event)
        team = event["team"]

        if event["type"] == "goal":
            if team == "home":
                self.active_match["home_score"] += 1
            else:
                self.active_match["away_score"] += 1
            self.momentum[team] = min(80, self.momentum[team] + 20)
            self.momentum["away" if team == "home" else "home"] = max(20, self.momentum["away" if team == "home" else "home"] - 15)

        stats_key = f"{team}_stats"
        if event["type"] in ("shot_on_target", "shot_off_target", "goal"):
            self.active_match[stats_key]["shots"] += 1
        if event["type"] in ("shot_on_target", "goal"):
            self.active_match[stats_key]["shots_on_target"] += 1
        if event["type"] == "foul":
            self.active_match[stats_key]["fouls"] += 1
        if event["type"] == "corner":
            self.active_match[stats_key]["corners"] += 1
        if event["type"] in ("yellow_card", "red_card"):
            self.active_match[stats_key]["cards"] += 1

        excitement = event.get("excitement", 3)
        self.momentum[team] = min(80, self.momentum[team] + excitement)
        other = "away" if team == "home" else "home"
        self.momentum[other] = max(20, self.momentum[other] - excitement // 2)

    def _update_momentum(self):
        for team in ["home", "away"]:
            decay = random.uniform(-2, 1)
            self.momentum[team] = max(20, min(80, self.momentum[team] + decay))

    def _update_possession(self):
        home_m = self.momentum["home"]
        home_poss = 40 + (home_m - 50) * 0.4 + random.uniform(-3, 3)
        home_poss = max(30, min(70, home_poss))
        self.active_match["home_stats"]["possession"] = round(home_poss)
        self.active_match["away_stats"]["possession"] = round(100 - home_poss)

    def _predict_next_event(self) -> dict:
        events = list(self.MATCH_EVENTS.keys())
        weights = [e["weight"] for e in self.MATCH_EVENTS.values()]
        predicted = random.choices(events, weights=weights)[0]
        minute_range = f"{self.active_match['minute'] + 1}-{min(90, self.active_match['minute'] + 10)}"
        return {"type": predicted, "expected_minute_range": minute_range, "probability": round(random.uniform(20, 60), 1)}

    def _energy_description(self, level: str) -> str:
        descriptions = {
            "electric": "MetLife Stadium is ROARING! The crowd is on their feet!",
            "excited": "Great atmosphere! Fans are engaged and vocal!",
            "engaged": "Steady energy throughout the stadium.",
            "calm": "A quieter moment in the match.",
            "quiet": "The stadium awaits the next big moment.",
        }
        return descriptions.get(level, "")


match_simulator = MatchSimulator()
