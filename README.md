# Chatbot Project with LLM APIs (OpenAI and Gemini)

This project implements two chatbots using different LLM (Large Language Model) APIs: OpenAI and Gemini. Each bot has specific capabilities and uses ChainLit for the UI implementation.

## 1. chatbot_using_openai

### Features:
- **Text, Image, and Audio Handling:** This bot can process text queries, images via URLs or base64 encoding, and audio files for transcription.
- **Historical Prompt Handling:** It can save and utilize historical prompts to enhance responses.
- **Integration with ChainLit:** Uses ChainLit for UI interaction.

### Functionality:
- **Text Handling:** Accepts text inputs and generates responses using OpenAI's chat completion API.
- **Image Handling:** Converts images to base64 format and includes them in responses.
- **Audio Handling:** Transcribes audio files using OpenAI's audio transcription service.

### Usage:
- Ensure dependencies are installed (see `requirements.txt`).
- Run the bot script (`chatbot_using_openai.py`) to start interacting via ChainLit UI.

## 2. chatbot_using_gemini

### Features:
- **Image and Text Handling:** This bot focuses on handling images and text queries.
- **No Audio Support:** Gemini API currently lacks audio processing capabilities for now.

### Functionality:
- **Image Handling:** Processes images and integrates them into responses.
- **Text Handling:** Responds to text queries using Gemini's capabilities.
- **Integration with ChainLit:** Utilizes ChainLit for UI interaction, similar to the OpenAI bot.

### Usage:
- Dependencies are listed in `requirements.txt`.
- Execute the bot script (`chatbot_using_gemini.py`) to interact with the UI provided by ChainLit.

## Dependencies

Ensure the following dependencies are installed using `pip install -r requirements.txt`:
- `openai`: For interacting with OpenAI's API.
- `gemini`: For using Gemini's API (specific installation instructions may vary).
- `chainlit`: For implementing the user interface.

## Getting Started

1. Clone this repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Add API key in the chatbot file you want to use.
3. Run `chatbot_using_openai.py` or `chatbot_using_gemini.py` based on your chosen bot.
4. Follow the prompts on the ChainLit UI to interact with the chatbot.

## Contributing

Contributions are welcome! If you'd like to enhance functionality, add features, or improve documentation, feel free to fork this repository and submit a pull request.

![Screen shot of bot processing image](image.png)
