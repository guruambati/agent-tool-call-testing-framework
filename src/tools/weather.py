"""
weather.py
==========
Mock weather tool with a fixed city database.
No real API calls — returns deterministic data for testing.

Supports celsius and fahrenheit unit conversion.
Raises KeyError for unknown cities.
Raises ValueError for invalid unit or empty city.
"""

from __future__ import annotations

from src.tools.base import BaseTool


# Fixed mock database — deterministic, no network required
WEATHER_DB: dict[str, dict] = {
    "new york":      {"temp_c": 12, "condition": "cloudy",   "humidity": 65, "wind_kph": 18},
    "london":        {"temp_c": 8,  "condition": "rainy",    "humidity": 82, "wind_kph": 22},
    "san francisco": {"temp_c": 17, "condition": "foggy",    "humidity": 75, "wind_kph": 14},
    "tokyo":         {"temp_c": 20, "condition": "sunny",    "humidity": 55, "wind_kph": 10},
    "sydney":        {"temp_c": 25, "condition": "sunny",    "humidity": 45, "wind_kph": 20},
    "berlin":        {"temp_c": 5,  "condition": "overcast", "humidity": 70, "wind_kph": 15},
    "hyderabad":     {"temp_c": 30, "condition": "hot",      "humidity": 40, "wind_kph": 8},
    "bangalore":     {"temp_c": 22, "condition": "pleasant", "humidity": 60, "wind_kph": 12},
}

VALID_UNITS = frozenset({"celsius", "fahrenheit"})


class WeatherTool(BaseTool):

    def __init__(self):
        super().__init__("weather")

    def run(self, city: str, unit: str = "celsius") -> dict:
        """
        Get current weather for a city.

        Args:
            city : city name (case-insensitive)
            unit : 'celsius' or 'fahrenheit'

        Returns:
            dict with keys: city, temp, unit, condition, humidity, wind_kph
        """
        params = {"city": city, "unit": unit}

        try:
            if not isinstance(city, str) or not city.strip():
                raise ValueError("'city' must be a non-empty string.")

            unit_lower = unit.lower().strip()
            if unit_lower not in VALID_UNITS:
                raise ValueError(
                    f"Invalid unit '{unit}'. Must be one of: {sorted(VALID_UNITS)}"
                )

            key  = city.lower().strip()
            data = WEATHER_DB.get(key)
            if data is None:
                raise KeyError(
                    f"No weather data for city '{city}'. "
                    f"Available: {sorted(WEATHER_DB.keys())}"
                )

            temp = data["temp_c"]
            if unit_lower == "fahrenheit":
                temp = round(temp * 9 / 5 + 32, 1)
            else:
                temp = float(temp)

            output = {
                "city":      city,
                "temp":      temp,
                "unit":      unit_lower,
                "condition": data["condition"],
                "humidity":  data["humidity"],
                "wind_kph":  data["wind_kph"],
            }
            self._record(params, output, success=True)
            return output

        except Exception as exc:
            self._record(params, None, success=False, error=str(exc))
            raise
