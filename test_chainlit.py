import os
from dotenv import load_dotenv
import google.generativeai as genai
import chainlit as cl
import json

load_dotenv()

with open("personas.json", "r") as f:
    personas = json.load(f)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@cl.on_chat_start
async def start():

    persona = personas["Alex"]

    system_prompt = f"""
    You are simulating a patient in a counseling training session.

    Name: {persona["name"]}
    Age: {persona["age"]}
    Gender: {persona["gender"]}
    Ethnicity: {persona["ethnicity"]}
    Background: {persona["background"]}
    Current struggle: {persona["current_struggle"]}
    Communication style: {persona["communication_style"]}
    Key symptoms: {", ".join(persona["key_symptoms"])}
    Primary concerns: {", ".join(persona["primary_concerns"])}

    Do not break character.
    Do not provide therapeutic advice; react realistically to the counselor's statements.
    """

    print("Creating Gemini chat...")

    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=system_prompt
    )

    chat_session = model.start_chat(history=[])

    cl.user_session.set("chat_session", chat_session)

    print("Gemini chat created!")


@cl.on_message
async def handle_message(message: cl.Message):

    print("1. Message received")

    chat_session = cl.user_session.get("chat_session")

    print("2. Chat session exists:", chat_session is not None)

    print("3. Sending to Gemini...")

    response = chat_session.send_message(message.content)

    print("4. Gemini responded!")

    await cl.Message(content=response.text).send()