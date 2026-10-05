from openai import OpenAI
import base64
import chainlit as cl

client = OpenAI(api_key='OPEN_AI_API_KEY')


def append_messages(image_url=None, query=None, audio_transcript=None):
    """
    Append messages based on provided parameters to OpenAI's chat completion API.

    Parameters:
    - image_url (str, optional): URL of the image to include in the message.
    - query (str, optional): Text query to append as a message.
    - audio_transcript (str, optional): Transcript of audio to append with the query.

    Returns:
    - str: Response message content from OpenAI's chat completion.
    """
    message_list = []

    if image_url:
        message_list.append({"type": "image_url", "image_url": {"url": image_url}})

    if query and not audio_transcript:
        message_list.append({"type": "text", "text": query})

    if audio_transcript:
        message_list.append({"type": "text", "text": query + "\n" + audio_transcript})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": message_list}],
        max_tokens=1024,
    )

    return response.choices[0].message.content


def image_to_base64(image_path):
    """
    Convert an image file to a base64 encoded string.

    Parameters:
    - image_path (str): Path to the image file.

    Returns:
    - str: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as img:
        encoded_string = base64.b64encode(img.read())
    return f"data:image/png;base64,{encoded_string.decode('utf-8')}"


def process_audio(audio_path):
    """
    Process audio file using OpenAI's transcription service.

    Parameters:
    - audio_path (str): Path to the audio file.

    Returns:
    - str: Transcription text of the audio.
    """
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
    return transcription.text


@cl.on_message
async def chat_handler(message: cl.Message):
    """
    Handle incoming messages, process images or audio if available, and send a response.

    Parameters:
    - message (cl.Message): Message object from ChainLit.

    Returns:
    - None
    """
    images = [file for file in message.elements if "image" in file.mime]
    audios = [file for file in message.elements if "audio" in file.mime]

    response_message = cl.Message(content="")

    if len(images) > 0:
        base64_image = image_to_base64(images[0].path)
        image_url = f"data:image/png;base64,{base64_image}"
        response = append_messages(image_url=image_url, query=message.content)

    elif len(audios) > 0:
        text = process_audio(audios[0].path)
        response = append_messages(query=message.content, audio_transcript=text)

    else:
        response = append_messages(query=message.content)

    response_message.content = response

    await response_message.send()
