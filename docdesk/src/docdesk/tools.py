# docdesk/tools.py  (updated)
"""Client-side tools for docdesk. Claude sees only name/description/input_schema."""

# --- Tool 1: upgraded to the 4-part description standard ---
WAREHOUSE_TOOL = {
    "name": "get_warehouse_value",
    "description": (
        # WHAT
        "Return the total current inventory value in USD for one warehouse. "
        # WHEN
        "Use when the user asks about the stock value, worth, or dollar total "
        "of a named warehouse. "
        # RETURNS
        "Returns a single formatted USD figure for the requested warehouse. "
        # CAVEAT
        "Does NOT return per-item breakdowns or quantities — only the total."
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

# --- Tool 2: new, fully specified ---
TICKET_TOOL = {
    "name": "get_customer_support_tickets",
    "description": (
        "Retrieve the most recent support tickets for a single customer by "
        "customer ID. Use this when the user asks about a customer's open "
        "issues, ticket history, or support status. Returns up to 10 recent "
        "tickets (status, subject, created date), newest first. Does NOT "
        "return billing or order data."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer's unique ID, e.g. 'CUST-40912'.",
            },
            "status": {
                "type": "string",
                "enum": ["open", "closed", "all"],  # exhaustive → no escape hatch needed
                "description": "Ticket status filter. Defaults to 'open'.",
            },
        },
        "required": ["customer_id"],
    },
}

TOOLS = [WAREHOUSE_TOOL, TICKET_TOOL]

# docdesk/tools.py  — add near the top
SENSITIVE_TOOLS = {"archive_shipment_logs", "delete_customer"}

def human_approves(name: str, tool_input: dict) -> bool:
    """Stub approval gate. In production: prompt a human via UI/Slack/email.
    Returns True only on explicit approval."""
    print(f"[APPROVAL NEEDED] {name}({tool_input}) — approve? [y/N]")
    return input().strip().lower() == "y"

# --- Implementations ---
def get_warehouse_value(warehouse_id: str) -> str:
    fake_db = {"A": 125_400.00, "B": 98_250.50, "C": 210_000.00}
    value = fake_db.get(warehouse_id.upper())
    if value is None:
        return f"ERROR: no warehouse named '{warehouse_id}'."
    return f"Warehouse {warehouse_id.upper()} total value: ${value:,.2f} USD"

def get_customer_support_tickets(customer_id: str, status: str = "open") -> str:
    fake = {
        "CUST-40912": [
            {"subject": "Login fails on mobile", "status": "open", "created": "2026-09-08"},
            {"subject": "Refund request", "status": "closed", "created": "2026-08-30"},
        ]
    }
    rows = fake.get(customer_id.upper())
    if rows is None:
        return f"ERROR: no customer '{customer_id}'."
    if status != "all":
        rows = [r for r in rows if r["status"] == status]
    if not rows:
        return f"No {status} tickets for {customer_id.upper()}."
    return "; ".join(f"[{r['status']}] {r['subject']} ({r['created']})" for r in rows)

# --- Dispatch table: the loop reads this; adding a tool needs NO loop change ---
TOOL_IMPLEMENTATIONS = {
    "get_warehouse_value": get_warehouse_value,
    "get_customer_support_tickets": get_customer_support_tickets,
}