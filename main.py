import random
from fastmcp import FastMCP
import json

# Create a FastMCP instance
mcp = FastMCP(name='Demo Server')

@mcp.tool()
def roll_dice(n_dice: int = 1) -> list[int]:
    """Roll n_dice 6-sided dice and return the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b

@mcp.resource("info://server")
def server_info():
    """Get information about the server"""
    info = {
        "name": "simple calculator"
    }
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)