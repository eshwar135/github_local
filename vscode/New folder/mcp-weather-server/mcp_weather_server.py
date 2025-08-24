import asyncio
from mcp.server.fast import FastMCPServer, tool

server = FastMCPServer("mcp-weather-server")

@tool()
async def get_weather(city: str) -> dict:
    """
    Returns simulated weather data for a city (Inspector testing phase).
    """
    return {
        "city": city,
        "temperature": "28°C",
        "condition": "Partly Cloudy",
        "humidity": "65%",
        "wind": "12 km/h"
    }

@server.resource("weather://{city}")
async def weather_resource(city: str):
    """
    Exposes weather data as a resource at weather://{city}.
    """
    data = await get_weather(city)
    return {
        "mimeType": "application/json",
        "data": data
    }

if __name__ == "__main__":
    asyncio.run(server.run())