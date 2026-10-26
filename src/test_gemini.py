import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"
response = client.models.generate_content(
    model=MODEL,
    contents="Reply with the single word: ready",
)
print(response.text)