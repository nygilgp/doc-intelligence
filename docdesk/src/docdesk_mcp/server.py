# docdesk_mcp/server.py
"""docdesk's shared MCP server. Exposes inventory as a TOOL, a warehouse
directory as a RESOURCE, and a summary PROMPT template — all three primitives."""
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("docdesk-inventory")

_DB = {"A": 125_400.00, "B": 98_250.50, "C": 210_000.00}

# --- TOOL: an action the model can call ---
@mcp.tool()
def get_warehouse_value(warehouse_id: str) -> str:
    """Return the total inventory value in USD for one warehouse.

    Use when the user asks about a warehouse's stock value or dollar total.
    Does NOT return per-item quantities.
    Args:
        warehouse_id: Warehouse code, e.g. 'A', 'B', 'C'.
    """
    v = _DB.get(warehouse_id.upper())
    return (f"Warehouse {warehouse_id.upper()}: ${v:,.2f} USD"
            if v is not None else f"ERROR: no warehouse '{warehouse_id}'.")

# --- RESOURCE: read-only data the client can fetch for context ---
@mcp.resource("inventory://warehouses")
def warehouse_directory() -> str:
    """The list of known warehouse codes (read-only reference data)."""
    return "Known warehouses: " + ", ".join(sorted(_DB))

# --- PROMPT: a reusable template that guides a task ---
@mcp.prompt()
def inventory_summary(warehouse_id: str) -> str:
    """Reusable template: ask for a concise inventory summary of a warehouse."""
    return (f"Summarize warehouse {warehouse_id}'s inventory value in one "
            f"sentence, then note if it's above or below $150,000.")

if __name__ == "__main__":
    mcp.run()   # stdio transport (local dev / Claude Code)