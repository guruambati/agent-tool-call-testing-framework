"""
test_weather.py
===============
12 tests covering: known cities, unit conversion, error paths,
response schema, and idempotency.
"""

import pytest
from src.tools.weather import WeatherTool


class TestWeatherHappyPath:

    def test_known_city_returns_data(self, weather):
        r = weather.run("London")
        assert r["city"] == "London"
        assert r["condition"] == "rainy"

    def test_celsius_unit_default(self, weather):
        r = weather.run("Tokyo")
        assert r["unit"] == "celsius"
        assert isinstance(r["temp"], float)

    def test_fahrenheit_conversion_correct(self, weather):
        r_c = weather.run("Tokyo", unit="celsius")
        r_f = weather.run("Tokyo", unit="fahrenheit")
        expected = round(r_c["temp"] * 9 / 5 + 32, 1)
        assert abs(r_f["temp"] - expected) < 0.01

    def test_response_has_all_required_fields(self, weather):
        r = weather.run("Sydney")
        for field in ("city", "temp", "unit", "condition", "humidity", "wind_kph"):
            assert field in r

    def test_case_insensitive_city_lookup(self, weather):
        r1 = weather.run("london")
        r2 = weather.run("LONDON")
        assert r1["temp"] == r2["temp"]

    def test_hyderabad_returns_hot(self, weather):
        r = weather.run("Hyderabad")
        assert r["condition"] == "hot"


class TestWeatherErrors:

    def test_unknown_city_raises_key_error(self, weather):
        with pytest.raises(KeyError, match="Atlantis"):
            weather.run("Atlantis")

    def test_invalid_unit_raises_value_error(self, weather):
        with pytest.raises(ValueError, match="unit"):
            weather.run("London", unit="kelvin")

    def test_empty_city_raises_value_error(self, weather):
        with pytest.raises(ValueError):
            weather.run("")

    def test_failed_calls_recorded(self, weather):
        with pytest.raises(KeyError):
            weather.run("Narnia")
        assert weather.call_count == 1
        assert weather.last_call.success is False


class TestWeatherIdempotency:

    def test_same_query_same_result(self, weather):
        r1 = weather.run("Berlin", unit="celsius")
        r2 = weather.run("Berlin", unit="celsius")
        assert r1["temp"] == r2["temp"]
        assert r1["condition"] == r2["condition"]

    def test_multiple_cities_independent(self, weather):
        r_london = weather.run("London")
        r_tokyo  = weather.run("Tokyo")
        assert r_london["condition"] != r_tokyo["condition"]
