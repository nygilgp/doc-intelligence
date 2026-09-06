"""Session hygiene for multi-turn support conversations.

The API is stateless (S1 E1), so WE carry history. This keeps it bounded so cost,
latency, and context don't grow without limit. (Compaction deepened in S4 E4.)
"""
MAX_TURNS = 20   # cap on retained turns before we trim

class Session:
    def __init__(self, max_turns: int = MAX_TURNS):
        self.messages: list[dict] = []
        self.max_turns = max_turns

    def add(self, role: str, content) -> None:
        self.messages.append({"role": role, "content": content})
        self._enforce_hygiene()

    def _enforce_hygiene(self) -> None:
        """Bound the history. For now: keep the most recent max_turns turns.
        (S4 E4 upgrades this to summarize/compact older turns instead of dropping.)"""
        if len(self.messages) > self.max_turns:
            self.messages = self.messages[-self.max_turns:]

    def reset(self) -> None:
        """Start a fresh session when a new task begins."""
        self.messages = []