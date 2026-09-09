"""memory_store.py — client-side handler for the memory tool (docdesk).

Connects to: agent.py (the agent requests memory ops; THIS executes them).
WHY: long reviews may be interrupted. The agent writes a progress log +
findings to /memories; a new session reads them and RESUMES. This is the
agent's insurance against a context reset.

SECURITY: every path is validated to stay inside the memory root — the
path-traversal protection the docs require (rejects /memories/../../secrets).
In production, swap the local base_path for an S3 prefix or DynamoDB keys.
"""
from pathlib import Path

MEMORY_ROOT = Path("./docdesk_memory").resolve()   # local demo; swap for S3 in prod


def _safe_path(requested: str) -> Path:
    """Reject path traversal — resolve and confirm it stays under MEMORY_ROOT.
    This is non-negotiable: without it, '/memories/../../secrets.env' escapes."""
    # Map the model's virtual '/memories' prefix onto our real root.
    rel = requested.replace("/memories", "", 1).lstrip("/")
    resolved = (MEMORY_ROOT / rel).resolve()
    if not resolved.is_relative_to(MEMORY_ROOT):        # Python 3.9+: the guard
        raise ValueError(f"Path traversal blocked: {requested}")
    return resolved


def handle_memory(command: str, **kwargs) -> str:
    """Execute a memory op the agent requested. Mirrors the doc'd commands."""
    if command == "view":
        p = _safe_path(kwargs["path"])
        if p.is_dir():
            files = "\n".join(f"{f.stat().st_size}\t{f}" for f in p.glob("*"))
            return f"Contents of {kwargs['path']}:\n{files}"
        return p.read_text() if p.exists() else f"The path {kwargs['path']} does not exist."
    if command == "create":
        p = _safe_path(kwargs["path"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(kwargs["file_text"])
        return f"File created successfully at: {kwargs['path']}"
    # str_replace / insert / delete / rename follow the same doc'd contract.
    return f"ERROR: unsupported command {command}"


if __name__ == "__main__":
    MEMORY_ROOT.mkdir(exist_ok=True)
    print(handle_memory("create", path="/memories/progress.md",
                        file_text="Reviewed sections 1-3. Next: section 4.\n"))
    print(handle_memory("view", path="/memories/progress.md"))
    # Traversal attempt is blocked:
    try:
        handle_memory("view", path="/memories/../../etc/passwd")
    except ValueError as e:
        print(e)