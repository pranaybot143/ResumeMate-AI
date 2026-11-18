import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

print("Testing Gemini 3.5 Flash Lite...")

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Explain artificial intelligence in two simple sentences."
)

print("\nGemini response:")
print(response.text)