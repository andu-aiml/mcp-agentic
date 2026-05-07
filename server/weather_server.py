from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
import requests

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"NWS Request Error: {e}")
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
    Event: {props.get("event", "Unknown")}
    Area: {props.get("areaDesc", "Unknown")}
    Severity: {props.get("severity", "Unknown")}
    Description: {props.get("description", "No description available")}
    Instructions: {props.get("instruction", "No specific instructions provided")}
    """



@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    Get severe weather alerts for a US state.

    IMPORTANT:
    Input must be a two-letter US state code.

    Examples:
    - CA = California
    - NY = New York
    - TX = Texas

    Do NOT pass full state names.
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Get detailed weather forecast for a latitude and longitude.

    Use this for:
    - weather conditions
    - temperature
    - wind
    - future forecasts
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
        {period["name"]}:
        Temperature: {period["temperature"]}°{period["temperatureUnit"]}
        Wind: {period["windSpeed"]} {period["windDirection"]}
        Forecast: {period["detailedForecast"]}
        """
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

@mcp.tool()
async def google_search(query: str) -> str:
    """
    Search the web for current information and general knowledge.

    Best for:
    - breaking news
    - recent events
    - politics
    - technology updates
    - sports results
    - factual lookups
    - public information

    The query should be concise and search-engine friendly.

    Good query examples:
    - "latest AI developments"
    - "US election news"
    - "Iran America conflict reason"
    - "weather California today"

    Avoid using this tool for:
    - mathematical calculations
    - logic reasoning
    - summarization of provided text
    """
    
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json"
    }

    async with httpx.AsyncClient(
        follow_redirects=True
        ) as client:
            response = await client.get(url, params=params)
            data = response.json()

    if "AbstractText" in data and data["AbstractText"]:
        return data["AbstractText"]

    return "No good results found"

@mcp.tool()
async def geocode_location(location: str) -> dict:
    """
    Convert a place name into latitude and longitude.
    """

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": USER_AGENT
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params=params,
            headers=headers
        )

        data = response.json()

    if not data:
        return {
            "error": "Location not found"
        }

    return {
        "latitude": data[0]["lat"],
        "longitude": data[0]["lon"],
        "display_name": data[0]["display_name"]
    }

def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()