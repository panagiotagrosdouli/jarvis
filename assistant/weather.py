import json
import os
import urllib.parse
import urllib.request


class WeatherService:
    def __init__(self):
        self.location = os.getenv("JARVIS_LOCATION", "Thessaloniki")

    def summary(self, location: str | None = None) -> str:
        city = (location or self.location).strip() or "Thessaloniki"
        encoded_city = urllib.parse.quote(city)
        url = f"https://wttr.in/{encoded_city}?format=j1"

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            current = data.get("current_condition", [{}])[0]
            temp = current.get("temp_C", "unknown")
            feels_like = current.get("FeelsLikeC", "unknown")
            humidity = current.get("humidity", "unknown")
            wind = current.get("windspeedKmph", "unknown")
            description = "weather unavailable"
            descriptions = current.get("weatherDesc") or []
            if descriptions:
                description = descriptions[0].get("value", description)

            recommendation = self._recommendation(description, temp)

            return (
                f"Weather for {city}: {temp}°C, feels like {feels_like}°C. "
                f"Condition: {description}. Humidity: {humidity}%. Wind: {wind} km/h. "
                f"Recommendation: {recommendation}"
            )
        except Exception:
            return (
                f"Weather is not available right now for {city}. "
                "Check your internet connection or set JARVIS_LOCATION in your .env file."
            )

    def _recommendation(self, description: str, temp_text: str) -> str:
        description_lower = description.lower()
        try:
            temp = int(float(temp_text))
        except Exception:
            temp = None

        if "rain" in description_lower or "shower" in description_lower:
            return "Take an umbrella."
        if "snow" in description_lower:
            return "Dress warmly and be careful outside."
        if temp is not None and temp >= 30:
            return "Take water with you and avoid staying too long in direct sun."
        if temp is not None and temp <= 10:
            return "Wear a warm jacket."
        return "The weather looks manageable. Dress comfortably."
