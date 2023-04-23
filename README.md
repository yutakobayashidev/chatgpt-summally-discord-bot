# chatgpt-summally-discord-bot

This Discord bot uses OpenAI's ChatGPT API to retrieve text from URLs included in messages that have been reacted to with the 🔍 emoji, and then responds with a summary of the text.

Also, for YouTube links, the transcript is read and summarized.

![Demo](https://user-images.githubusercontent.com/91340399/232278806-e6275b49-329a-4fe7-86eb-8b71beda4c92.png)

## Usage

### environment variables

1. Rename the `.env.example` file and change it to `.env`.

2. Generate an API token from the [OpenAI website](https://platform.openai.com/account/api-keys).

3. Create a bot from [Discord Developer Portal](https://discord.com/developers/applications) and copy the token.

```bash
OPENAI_API_KEY="for"
DISCORD_TOKEN="bar"
```

### install dependencies

Install dependencies with pip.

```bash
pip install -r requirements.txt
```

### run

```bash
python bot.py
```
