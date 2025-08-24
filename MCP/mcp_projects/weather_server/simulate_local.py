sim_code = r'''
"""
🔧 MCP Plugin Dev Prompt: mcp-weather-server
Phase: Inspector-only testing
Goal: Validate get_weather(city) tool via weather://{city} resource
"""

# Plugin metadata
plugin_name = "mcp-weather-server"
tool_name = "get_weather"
resource_uri = "weather://{city}"

# Sample test cities
cities = ["Bengaluru", "Tokyo", "New York", "London", "Sydney"]

# Simulated tool logic (replace with actual MCP binding later)
def get_weather(city):
    uri = resource_uri.format(city=city)
    print(f"🛰️ Tool Call → {tool_name}('{city}') → {uri}")
    # Simulated response
    return {
        "city": city,
        "temperature": "28°C",
        "condition": "Partly Cloudy",
        "humidity": "65%",
        "wind": "12 km/h"
    }

# Run tests
for city in cities:
    result = get_weather(city)
    print(f"🌦️ {city} → {result}\n")

# 🧩 Next Step: Once stable, bind tool to Claude Desktop via MCP SDK.
# Validate mcp.json, isolate environment, and register kernel cleanly.
'''
sim_path = project_dir / "simulate_local.py"
sim_path.write_text(sim_code, encoding="utf-8")
print("Wrote:", sim_path)
