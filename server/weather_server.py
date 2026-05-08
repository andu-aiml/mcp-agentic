from typing import Any
from tavily import TavilyClient
import httpx
from mcp.server.fastmcp import FastMCP
import requests
import logging
import os
from dotenv import load_dotenv
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("my-server")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

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

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def tavily_search_sync(query):

    return tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=3
    )

@mcp.tool()
async def google_search(query: str) -> dict:
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

    Use this tool whenever up-to-date internet
    information is required.
    """

    try:

        response = await asyncio.to_thread(
            tavily_search_sync,
            query
        )

        return {
            "status": "success",
            "results": response.get("results", [])
        }

    except Exception as e:

        logger.error(f"Tavily Search Error: {e}")

        return {
            "status": "error",
            "message": str(e)
        }
    
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