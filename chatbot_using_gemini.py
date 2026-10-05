import os
import json
import PIL.Image
from dotenv import load_dotenv
import google.generativeai as genai
import chainlit as cl


# load environment variables from .env file
load_dotenv()

# load json file with client personas
with open("personas.json", "r") as f:
    personas = json.load(f)

# set up gemini api
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


#creates and returns end session button
def get_end_session_action():
    """Returns the End Session button action with required Pydantic payload."""
    return [
        cl.Action( #Action is button that user can click
            name="end_session",
            value="end_session",
            label="🛑 End Session & Get Feedback",
            payload={"action": "end_session"}
        )
    ]


# runs when new chat session starts
@cl.on_chat_start
async def start():

    # Create the dropdown
    selected = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="persona",
                label="Select Patient Persona",
                values=[
                    persona["name"]
                    for persona in personas.values()
                ],
                initial_value=list(personas.values())[0]["name"]
            )
        ]
    ).send()

    # get name of the persona the counselor selected
    persona_id = selected["persona"]

    # get the patient's info
    persona = personas[persona_id]

    # creating system prompt
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

    # Initialize the generative model and start the chat
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=system_prompt
    )

    chat_session = model.start_chat(history=[])

    # Save the Gemini chat session for this user
    cl.user_session.set("chat_session", chat_session)

    # Initialize the conversation history
    cl.user_session.set("messages", [])

    # Track whether the session has ended
    cl.user_session.set("session_ended", False)

    # Save the system prompt
    cl.user_session.set("system_prompt", system_prompt)

    # Save current persona name for the feedback prompt
    cl.user_session.set("persona_name", persona["name"])

    print(f"\n[SESSION START] Conversation history initialized for persona: {persona['name']}")
    print(f"[SESSION START] Initial history length: {len(cl.user_session.get('messages'))}\n")

    # Send initial welcome message with the End Session button
    await cl.Message(
        content=f"**Session started with {persona['name']}.** You may begin the counseling session. Click below when you are ready to conclude and generate clinical feedback.",
        actions=get_end_session_action() #the end session button
    ).send()


def load_image(image_path):
    """
    Load an image from the specified path using PIL.

    Args:
        image_path (str): The path to the image file.

    Returns:
        PIL.Image: The loaded image object.
    """
    image = PIL.Image.open(image_path)
    return image


@cl.on_message
async def handle_message(message: cl.Message):
    """
    Process incoming messages, handle images, and respond using a generative AI model.

    Args:
        message (str): The incoming message object.
    """
    # Block inputs if the session has already been ended
    if cl.user_session.get("session_ended"):
        await cl.Message(
            content="⚠️ This session has ended. Change persona settings to start a new session."
        ).send()
        return

    try:
        print("1. Message received:", message.content)

        chat_session = cl.user_session.get("chat_session")

        print("2. Chat session exists:", chat_session is not None)

        # Make sure the chat session is initialized
        if chat_session is None:
            print("ERROR: chat_session is not initialized!")
            await cl.Message(
                content="Error: Gemini chat session was not initialized."
            ).send()
            return

        # Get the current conversation history
        messages = cl.user_session.get("messages", []) #if there isnt one, get empty list

        # Save the counselor's message
        messages.append({
            "role": "Counselor",
            "content": message.content
        })

        cl.user_session.set("messages", messages)
        print(f"\n[HISTORY UPDATE] User message saved. Total turns: {len(messages)}")

        # Prepare the prompt
        prompt = message.content

        # Check for an attached image
        image_files = [
            file for file in message.elements
            if "image" in file.mime
        ]

        if image_files:
            image = load_image(image_files[0].path)
            prompt = [prompt, image]

        print("3. Sending request to Gemini...")

        # Send the message to Gemini
        response = chat_session.send_message(prompt)

        print("4. Gemini responded:", response.text[:200])

        # Save the simulated patient's response
        messages.append({
            "role": "Patient",
            "content": response.text
        })

        cl.user_session.set("messages", messages)

        print(f"\n[HISTORY UPDATE] Assistant response saved. Total turns: {len(messages)}")
        print("=== UPDATED CONVERSATION HISTORY ===")
        print(json.dumps(messages, indent=2))
        print("===================================\n")

        # Display the response with the End Session button
        await cl.Message(
            content=response.text,
            actions=get_end_session_action()
        ).send()

    except Exception as e:
        print(f"[ERROR] Exception raised during message handling: {e}")
        error_message = cl.Message(
            content=f"An error occurred: {str(e)}"
        )
        await error_message.send()


@cl.on_settings_update
async def setup_agent(settings):

    # Get the selected persona
    persona_id = settings["persona"]

    # Get the patient's information
    persona = personas[persona_id]

    # Create the system prompt
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

    # Create a new Gemini model using the selected persona
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=system_prompt
    )

    # Start a new conversation
    chat_session = model.start_chat(history=[])

    # Save the new Gemini chat session
    cl.user_session.set("chat_session", chat_session)

    # Reset the conversation history
    cl.user_session.set("messages", [])

    # Reset the session status
    cl.user_session.set("session_ended", False)

    # Save the new system prompt
    cl.user_session.set("system_prompt", system_prompt)

    # Save current persona name
    cl.user_session.set("persona_name", persona["name"])

    print(f"\n[SETTINGS UPDATE] Persona changed to: {persona['name']}")
    print("[SETTINGS UPDATE] Conversation history reset to empty list: []\n")

    await cl.Message(
        content=f"**Persona updated to {persona['name']}.** Session history has been reset.",
        actions=get_end_session_action()
    ).send()


# PHASE 4: Automated Feedback Generation Triggered by End Session Button
@cl.action_callback("end_session")
async def on_end_session(action: cl.Action):
    """
    Triggered when the counselor clicks 'End Session & Get Feedback'.
    """
    # Lock the session state
    cl.user_session.set("session_ended", True)

    messages = cl.user_session.get("messages", [])
    persona_name = cl.user_session.get("persona_name", "the patient")

    if not messages:
        await cl.Message(
            content="⚠️ No conversation transcript found to evaluate. Please exchange messages with the patient first."
        ).send()
        return

    # Compile the transcript string
    formatted_transcript = ""
    for msg in messages:
        formatted_transcript += f"**{msg['role']}**: {msg['content']}\n\n"

    # Define the feedback prompt for the Senior Clinical Supervisor
    eval_prompt = f"""
    You are an expert Senior Clinical Supervisor evaluating a trainee counselor's performance.

    Review the following transcript from a counseling simulation session with patient '{persona_name}':

    --- TRANSCRIPT ---
    {formatted_transcript}
    --- END TRANSCRIPT ---

    Provide structured feedback in Markdown under the following explicit sections:

    ### 1. Active Listening & Empathy
    - Evaluate how effectively the counselor validated feelings and demonstrated empathy.

    ### 2. Open-Ended Questioning
    - Assess whether the counselor asked open-ended questions that encouraged the patient to elaborate.

    ### 3. Safety & Ethics
    - Evaluate how well potential risks, boundaries, and ethical concerns were identified and managed.

    ### 4. Areas for Improvement & Actionable Recommendations
    - Detail specific alternative phrasing or strategies the counselor could have used to improve outcomes.

   Include a rating for each of these categories out of 10. Keep each section max 2 sentences long and relatively concise
    """

    # Generate the feedback report inside a loading step
    async with cl.Step(name="Generating Supervisor Evaluation...") as step:
        step.output = "Analyzing transcript..."

        eval_model = genai.GenerativeModel(model_name="gemini-3.8-flash")
        feedback_response = eval_model.generate_content(eval_prompt)

        step.output = "Evaluation complete!"

    # Display the final feedback report
    await cl.Message(
        content=f"# 📋 Senior Clinical Supervisor Feedback Report\n\n{feedback_response.text}"
    ).send()