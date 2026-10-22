# test_claude.py
# Sends one test message to Claude to check the connection.

from dotenv import load_dotenv
import anthropic

load_dotenv()                    # open the locked drawer (.env)
client = anthropic.Anthropic()   # finds your key automatically

response = client.messages.create(
    model="claude-haiku-5-5",    # the small, low-cost model
    max_tokens=100,              # caps the reply length (and cost)
    messages=[
        {"role": "user", "content": "In one sentence, what is an AI agent?"}
    ],
)

print(response.content[0].text)