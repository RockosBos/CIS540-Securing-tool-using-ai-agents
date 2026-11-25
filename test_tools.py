import ollama

def send_message(recipient: str, body: str) -> str:
    """Send a message to a recipient."""
    return f"(mock) sent to {recipient}"

response = ollama.chat(
    model="qwen3:8b",
    messages=[{"role": "user",
               "content": "Send a message to alice@example.com saying the meeting is at 3pm."}],
    tools=[send_message],          # the library builds the schema from the function
    options={"temperature": 0},
)

print(response.message.tool_calls)