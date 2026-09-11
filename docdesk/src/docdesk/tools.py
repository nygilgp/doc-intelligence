# docdesk/tools.py
"""Client-side tools for docdesk. Each tool = a schema Claude sees +
a Python function your code runs. Claude never runs these itself."""

# --- 1. The schema Claude sees (name / description / input_schema) ---
WAREHOUSE_TOOL = {
    "name": "get_warehouse_value",
    "description": (
        "Return the total current inventory value in USD for a single "
        "warehouse. Use when the user asks about stock value, worth, or "
        "totals for a named warehouse. Requires the warehouse code."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "warehouse_id": {
                "type": "string",
                "description": "Warehouse code, e.g. 'A', 'B', 'C'.",
            }
        },
        "required": ["warehouse_id"],
    },
}

TOOLS = [WAREHOUSE_TOOL]

# --- 2. The real code your app runs (stubbed; swap for a live REST call) ---
def get_warehouse_value(warehouse_id: str) -> str:
    fake_db = {"A": 125_400.00, "B": 98_250.50, "C": 210_000.00}
    value = fake_db.get(warehouse_id.upper())
    if value is None:
        # Signal a recoverable error to Claude (full pattern in S5E3)
        return f"ERROR: no warehouse named '{warehouse_id}'."
    return f"Warehouse {warehouse_id.upper()} total value: ${value:,.2f} USD"

# --- 3. Dispatch table: map tool name -> function ---
TOOL_IMPLEMENTATIONS = {
    "get_warehouse_value": get_warehouse_value,
}