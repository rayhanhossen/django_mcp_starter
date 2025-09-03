import aiohttp
from typing import Dict, Any

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

async def get_weather(place: str) -> Dict[str, Any]:
    """
    Fetch current weather for a given place name.

    Args:
        place: City or location name (e.g., "Dhaka").

    Returns:
        Dict with current weather data or error message.
    """
    if not place or not isinstance(place, str):
        return {"response": False, "error": "Place name must be a non-empty string"}

    try:
        async with aiohttp.ClientSession() as session:
            # 1) Geocode place → lat/lon
            async with session.get(GEOCODE_URL, params={"name": place, "count": 1}, timeout=10) as geo_resp:
                if geo_resp.status != 200:
                    return {"response": False, "error": f"Geocoding failed: HTTP {geo_resp.status}"}
                geo_data = await geo_resp.json()
                results = geo_data.get("results")
                if not results:
                    return {"response": False, "error": f"No location found for '{place}'"}
                lat = results[0]["latitude"]
                lon = results[0]["longitude"]

            # 2) Get current weather
            async with session.get(WEATHER_URL, params={"latitude": lat, "longitude": lon, "current_weather": "true"}, timeout=10) as weather_resp:
                if weather_resp.status != 200:
                    return {"response": False, "error": f"Weather fetch failed: HTTP {weather_resp.status}"}
                weather_data = await weather_resp.json()
                current = weather_data.get("current_weather")
                if not current:
                    return {"response": False, "error": "No current weather data available"}

                return {
                    "response": True,
                    "data": {
                        "place": results[0]["name"],
                        "country": results[0].get("country"),
                        "latitude": lat,
                        "longitude": lon,
                        **current
                    }
                }

    except Exception as e:
        return {"response": False, "error": f"Weather API error: {e}"}
