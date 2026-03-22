import os
import discord
import requests
import random
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

print("TOKEN =", TOKEN)
print("CHANNEL_ID =", CHANNEL_ID)

if not TOKEN:
    raise Exception("❌ TOKEN manquant (Railway Variables)")

CHANNEL_ID = int(CHANNEL_ID)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def get_meme():
    try:
        url = "https://www.reddit.com/r/yugiohmemes/top.json?limit=50&t=day"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers)
        data = res.json()

        posts = data["data"]["children"]

        images = [
            p["data"]["url"]
            for p in posts
            if p["data"]["url"].endswith((".jpg", ".png", ".jpeg"))
        ]

        if not images:
            return None

        return random.choice(images)

    except Exception as e:
        print("❌ Erreur meme:", e)
        return None


@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Salon introuvable")
        return

    while True:
        meme = get_meme()

        if meme:
            embed = discord.Embed(title="😂 Meme Yu-Gi-Oh")
            embed.set_image(url=meme)
            await channel.send(embed=embed)
        else:
            print("❌ Aucun meme trouvé")

        await asyncio.sleep(1800)  # 30 minutes


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "!meme":
        meme = get_meme()
        if meme:
            await message.channel.send(meme)
        else:
            await message.channel.send("❌ Aucun meme trouvé")


client.run(TOKEN)
