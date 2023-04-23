import re
import discord
import requests
import openai
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv(verbose=True)
openai.api_key = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)


@client.event
async def on_raw_reaction_add(payload):
    text_channel = client.get_channel(payload.channel_id)
    message = await text_channel.fetch_message(payload.message_id)

    if payload.emoji.name == "🔍":
        print("Reaction recognized: 🔍")
        url = extract_url_from_message(message.content)
        if url is None:
            await message.reply("URL not detected.")
            return

        summary, cost = summarize_and_translate(url)

        if summary is None or cost is None:
            await message.reply("Failed to parse the HTML.")
        else:
            print("Replying with summary...")
            await message.reply(f"{summary}\n\nAPI usage cost: {cost:.4f}$")
            print("Replied with summary.")


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


def extract_url_from_message(content):
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    urls = re.findall(url_pattern, content)
    return urls[0] if urls else None


def ask_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "入力された文章を要約してください。\n制約条件\n・文章は簡潔にわかりやすく。\n・箇条書きで3行以内で出力。\n・1行あたりの文字数は80文字程度。\n・重要なキーワードは取り逃がさない。\n・要約した文章は日本語へ翻訳。"},
                {"role": "user", "content": prompt},
            ],
        )

        message = response["choices"][0]["message"]["content"]
        tokens_used = int(response["usage"]["total_tokens"])
        return message, tokens_used
    except Exception as e:
        raise Exception(e)


def summarize_and_translate(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    match = re.search(
        "^https?://(?:www\.)?(?:youtu\.be/|youtube\.com/watch\?v=)([\w-]+)", url)
    if match:
        video_id = match.group(1)

        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["ja", "en"])

            transcript = convert_transcript_list(
                transcript_list) if transcript_list else []

            summary, tokens_used = ask_gpt(transcript)
            cost = tokens_used * 0.000002

            return summary, cost
        except:
            return None, None
    else:
        print("No video ID found")

        main_content = find_main_content(soup)

        if not main_content:
            print("🚩 Failed to parse the HTML")
            return None, None

        content = extract_text_from_content(main_content)
        if not content:
            print("🚩 Failed to parse the HTML")
            return None, None
        print(f"Content length: {len(content)} characters")
        summary, tokens_used = ask_gpt(content)
        cost = tokens_used * 0.000002

        return summary, cost


def convert_transcript_list(transcript_list):
    return ''.join(v['text'] for v in transcript_list)


def find_main_content(soup):
    for tag in ['article', 'main', 'div']:
        main_content = soup.find(tag)
        if main_content:
            break
    return main_content


def extract_text_from_content(content):
    paragraphs = content.find_all('p')
    if not paragraphs:
        return None
    return ' '.join([p.get_text() for p in paragraphs])


client.run(os.getenv("DISCORD_TOKEN"))
