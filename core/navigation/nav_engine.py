"""Advanced Navigation Engine with pathfinding and accessibility routing."""
from typing import Any


class NavigationEngine:
    """Provides intelligent wayfinding with crowd-aware and accessible routes."""

    FACILITIES = {
        "entrances": [
            {"id": "E1", "name": "Main Gate North", "lat": 40.8135, "lon": -74.0745, "accessible": True, "crowd": "low"},
            {"id": "E2", "name": "Gate East", "lat": 40.8128, "lon": -74.0730, "accessible": True, "crowd": "medium"},
            {"id": "E3", "name": "Gate South", "lat": 40.8120, "lon": -74.0745, "accessible": True, "crowd": "low"},
            {"id": "E4", "name": "VIP Entrance", "lat": 40.8128, "lon": -74.0760, "accessible": True, "crowd": "low"},
        ],
        "restrooms": [
            {"id": "R1", "name": "Restroom North", "lat": 40.8132, "lon": -74.0742, "accessible": True, "wait_time": 2, "floor": 1},
            {"id": "R2", "name": "Restroom East", "lat": 40.8128, "lon": -74.0733, "accessible": True, "wait_time": 5, "floor": 1},
            {"id": "R3", "name": "Restroom South", "lat": 40.8122, "lon": -74.0742, "accessible": False, "wait_time": 3, "floor": 1},
            {"id": "R4", "name": "Restroom West (VIP)", "lat": 40.8128, "lon": -74.0757, "accessible": True, "wait_time": 1, "floor": 2},
        ],
        "food_court": [
            {"id": "F1", "name": "Food Court North", "lat": 40.8133, "lon": -74.0745, "cuisine": ["American", "Mexican"], "wait_time": 8, "rating": 4.2, "price": "$$"},
            {"id": "F2", "name": "Food Court East", "lat": 40.8128, "lon": -74.0728, "cuisine": ["Asian", "Italian"], "wait_time": 12, "rating": 4.5, "price": "$$$"},
            {"id": "F3", "name": "Food Court South", "lat": 40.8121, "lon": -74.0745, "cuisine": ["Halal", "Vegan", "Kosher"], "wait_time": 5, "rating": 4.0, "price": "$"},
            {"id": "F4", "name": "Food Court West", "lat": 40.8128, "lon": -74.0762, "cuisine": ["Burgers", "Pizza", "Craft Beer"], "wait_time": 10, "rating": 4.3, "price": "$$"},
        ],
        "merchandise": [
            {"id": "M1", "name": "Team Store North", "lat": 40.8134, "lon": -74.0743, "items": ["Jerseys", "Scarves", "Collectibles"]},
            {"id": "M2", "name": "Fan Shop East", "lat": 40.8128, "lon": -74.0731, "items": ["Jerseys", "Hats", "Flags"]},
        ],
        "medical": [
            {"id": "MED1", "name": "Medical Station North", "lat": 40.8133, "lon": -74.0744, "staff": 3, "equipment": ["First Aid", "AED", "Wheelchair"]},
            {"id": "MED2", "name": "Medical Station South", "lat": 40.8122, "lon": -74.0744, "staff": 2, "equipment": ["First Aid", "AED"]},
        ],
        "recycling": [
            {"id": "RC1", "name": "Eco Station North", "lat": 40.8134, "lon": -74.0744, "types": ["Plastic", "Paper", "Glass"], "points": 50},
            {"id": "RC2", "name": "Eco Station East", "lat": 40.8128, "lon": -74.0732, "types": ["Plastic", "Paper"], "points": 30},
            {"id": "RC3", "name": "Eco Station South", "lat": 40.8121, "lon": -74.0744, "types": ["Plastic", "Paper", "Glass", "Food Waste"], "points": 75},
        ],
    }

    ACCESSIBILITY_PROFILES = {
        "wheelchair": {"needs": ["ramp", "elevator"], "avoid": ["stairs"], "max_slope": 8},
        "visual_impairment": {"needs": ["audio_guide", "braille", "companion"], "avoid": []},
        "hearing_impairment": {"needs": ["visual_alerts", "sign_language", "captioning"], "avoid": []},
        "elderly": {"needs": ["short_distance", "rest_areas", "handrails"], "avoid": ["steep_ramp"]},
    }

    def find_nearest(self, lat: float, lon: float, facility_type: str, accessible_only: bool = False) -> dict | None:
        """Find nearest facility of a given type."""
        facilities = self.FACILITIES.get(facility_type, [])
        if not facilities:
            return None

        best = None
        best_dist = float("inf")

        for f in facilities:
            if accessible_only and not f.get("accessible", False):
                continue
            dist = ((f["lat"] - lat) ** 2 + (f["lon"] - lon) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best = {**f, "distance_km": round(dist * 111, 2)}

        return best

    def get_directions(self, origin_id: str, dest_id: str, mode: str = "standard") -> dict:
        """Get detailed directions between two points."""
        origin = self._find_facility(origin_id)
        dest = self._find_facility(dest_id)

        if not origin or not dest:
            return {"error": "Invalid origin or destination"}

        dlat = dest["lat"] - origin["lat"]
        dlon = dest["lon"] - origin["lon"]
        distance = ((dlat ** 2 + dlon ** 2) ** 0.5) * 111
        time_min = max(1, round(distance * 12))

        steps = self._generate_steps(origin, dest, mode, dlat, dlon)

        return {
            "origin": origin["name"],
            "destination": dest["name"],
            "distance_km": round(distance, 2),
            "estimated_time_min": time_min,
            "mode": mode,
            "steps": steps,
            "accessibility_note": "Accessible route with ramp/elevator" if mode == "accessible" else None,
        }

    def get_crowd_aware_route(self, origin_id: str, dest_id: str, zone_densities: dict) -> dict:
        """Get route that avoids high-density zones."""
        route = self.get_directions(origin_id, dest_id)

        crowdest = max(
            zone_densities.items(),
            key=lambda x: x[1].get("percentage", 0),
            default=(None, {"percentage": 0}),
        )

        if crowdest[0] and crowdest[1].get("percentage", 0) > 75:
            zone_name = crowdest[1].get("name", crowdest[0])
            pct = crowdest[1]["percentage"]
            route["warning"] = f"Avoid {zone_name} — at {pct}% capacity"
            route["alternative_route"] = "Use outer concourse to bypass congested area"
            route["estimated_time_min"] += 3

        return route

    def get_nearby_options(self, lat: float, lon: float, facility_type: str, count: int = 3) -> list:
        """Get multiple nearby facilities sorted by distance."""
        facilities = self.FACILITIES.get(facility_type, [])
        results = []

        for f in facilities:
            dist = ((f["lat"] - lat) ** 2 + (f["lon"] - lon) ** 2) ** 0.5
            results.append({
                **f,
                "distance_km": round(dist * 111, 2),
                "walking_time_min": max(1, round(dist * 111 * 12)),
            })

        results.sort(key=lambda x: x["distance_km"])
        return results[:count]

    def get_accessibility_info(self, profile: str) -> dict:
        """Get accessibility information for a specific profile."""
        profile_data = self.ACCESSIBILITY_PROFILES.get(profile, {})
        accessible_facilities = {}

        for ftype, facilities in self.FACILITIES.items():
            accessible = [f for f in facilities if f.get("accessible", False)]
            if accessible:
                accessible_facilities[ftype] = accessible

        return {
            "profile": profile,
            "needs": profile_data.get("needs", []),
            "accessible_facilities": accessible_facilities,
            "assistance_available": [
                "Staff escort from any entrance",
                "Companion seating in all zones",
                "Audio guide in 10 languages",
                "Tactile paving on main routes",
                "Emergency call points every 50m",
            ],
            "tips": [
                "Arrive early for best accessible seating",
                "Download StadiumIQ app for turn-by-turn navigation",
                "Request sign language interpreter 24h before event",
            ],
        }

    def _find_facility(self, facility_id: str):
        for facilities in self.FACILITIES.values():
            for f in facilities:
                if f["id"] == facility_id:
                    return f
        return None

    def _generate_steps(self, origin: dict, dest: dict, mode: str, dlat: float, dlon: float) -> list:
        steps = []
        step_num = 1

        if dlat > 0.0003:
            steps.append({"step": step_num, "instruction": "Head north along the concourse", "distance": "50m"})
            step_num += 1
        elif dlat < -0.0003:
            steps.append({"step": step_num, "instruction": "Head south along the concourse", "distance": "50m"})
            step_num += 1

        if dlon > 0.0003:
            steps.append({"step": step_num, "instruction": "Continue east through the main walkway", "distance": "80m"})
            step_num += 1
        elif dlon < -0.0003:
            steps.append({"step": step_num, "instruction": "Continue west through the main walkway", "distance": "80m"})
            step_num += 1

        if mode == "accessible":
            steps.append({"step": step_num, "instruction": "Use ramp/elevator at transition point", "distance": "10m"})
            step_num += 1
            steps.append({"step": step_num, "instruction": "Follow blue accessibility signage", "distance": "40m"})
            step_num += 1

        steps.append({"step": step_num, "instruction": f"Arrive at {dest['name']}", "distance": "0m"})

        return steps


navigation_engine = NavigationEngine()
