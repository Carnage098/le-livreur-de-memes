import os
import discord
import requests
import random
import asyncio
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

if not TOKEN:
    raise Exception("❌ TOKEN manquant (Railway Variables)")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 🔥 mémoire
sent_memes = []
meme_stats = {"sent": 0}

# 🔀 plusieurs sources
SUBREDDITS = [
    "yugiohmemes",
    "YuGiOhMemes",
    "masterduel"
]

def get_meme():
    try:
        subreddit = random.choice(SUBREDDITS)
        url = f"https://www.reddit.com/r/{subreddit}/top.json?limit=50&t=day"
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

        random.shuffle(images)

        for img in images:
            if img not in sent_memes:
                sent_memes.append(img)
                if len(sent_memes) > 50:
                    sent_memes.pop(0)
                return img

        return None

    except Exception as e:
        print("❌ Erreur meme:", e)
        return None


def create_embed(meme_url):
    messages = [
        "📦 Livraison express de memes !",
        "🚚 Le livreur débarque avec un colis !",
        "😂 Meme fraîchement livré !",
        "🔥 Meme rare trouvé sur le terrain !",
        "⚡ Invocation spéciale d’un meme !"
    ]

    embed = discord.Embed(
        title=random.choice(messages),
        color=discord.Color.random()
    )
    embed.set_image(url=meme_url)
    embed.set_footer(text=f"📊 Memes livrés : {meme_stats['sent']}")
    return embed


async def send_meme(channel):
    meme = get_meme()

    if meme:
        meme_stats["sent"] += 1
        embed = create_embed(meme)
        msg = await channel.send(embed=embed)

        # 👍👎 réactions
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
    else:
        await channel.send("❌ Le livreur n’a rien trouvé...")


# 🚀 BOT READY
@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")

    await tree.sync()

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Salon introuvable")
        return

    while True:
        await send_meme(channel)
        await asyncio.sleep(1800)  # 30 min


# 💬 commande texte
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "!meme":
        await send_meme(message.channel)


# ⚡ commande slash
@tree.command(name="meme", description="Recevoir un meme Yu-Gi-Oh")
async def meme_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    await send_meme(interaction.channel)


client.run(TOKEN)
