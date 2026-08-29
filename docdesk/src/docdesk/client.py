"""Core Claude client for the Document Intelligence & Support Application."""
from anthropic import Anthropic

# One shared client. Reads ANTHROPIC_API_KEY from the environment.
_client = Anthropic()

# Pin the model in one place (S1 E22 will formalize version pinning).
DEFAULT_MODEL = "claude-sonnet-4-5"


def ask(question: str, max_tokens: int = 1024) -> str:
    """Send a single user question to Claude and return the text reply.

    Stateless: this call carries no history. Multi-turn memory comes later
    (we'll pass a full messages list once we add conversation handling).
    """
    resp = _client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": question}],
    )
    return resp.content[0].text


if __name__ == "__main__":
    print(ask("In one sentence, what is a stateless API?"))