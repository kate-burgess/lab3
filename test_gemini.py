import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.8-flash")

print("1. Creating chat...")
chat_session = model.start_chat(history=[])

print("2. Sending message...")
response = chat_session.send_message("Hi, how are you?")

print("3. Gemini responded!")
print(response.text)