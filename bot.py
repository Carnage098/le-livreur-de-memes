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

# 🔀 subreddits 100% memes
SUBREDDITS = [
    "yugiohmemes",
    "YuGiOhMemes"
]

# 🧠 récupération filtrée
def get_meme():
    try:
        subreddit = random.choice(SUBREDDITS)
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=50"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers)
        data = res.json()

        posts = data["data"]["children"]

        images = []

        for p in posts:
            post = p["data"]

            # 🧠 filtre titre (meme uniquement)
            title = post.get("title", "").lower()
            if not any(word in title for word in ["meme", "funny", "joke", "lol"]):
                continue

            # 🖼️ récupération image fiable
            if "preview" in post:
                try:
                    img = post["preview"]["images"][0]["source"]["url"]
                    img = img.replace("&amp;", "&")
                    images.append(img)
                except:
                    continue

        print(f"📸 Images trouvées (filtrées): {len(images)}")

        # 🛟 fallback si rien trouvé
        if not images:
            return "https://i.imgur.com/3ZUrjUP.jpeg"

        random.shuffle(images)

        # 🚫 anti-doublons
        for img in images:
            if img not in sent_memes:
                sent_memes.append(img)
                if len(sent_memes) > 50:
                    sent_memes.pop(0)
                return img

        return random.choice(images)

    except Exception as e:
        print("❌ Erreur meme:", e)
        return "https://i.imgur.com/3ZUrjUP.jpeg"


# 🎨 embed stylé
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


# 🚚 envoyer meme
async def send_meme(channel):
    meme = get_meme()

    meme_stats["sent"] += 1
    embed = create_embed(meme)
    msg = await channel.send(embed=embed)

    # 👍👎 réactions
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


# 🚀 bot prêt
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
