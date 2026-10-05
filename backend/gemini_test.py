from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(api_key))

client = genai.Client(api_key=api_key)

response = client.interactions.create(
    model="gemini-3.8-flash",
    input="Say hello"
)

print(response.output_text)