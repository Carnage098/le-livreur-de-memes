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

# 🔥 mémoire anti-doublons
sent_memes = set()
meme_stats = {"sent": 0}

# 🔀 subreddits
SUBREDDITS = [
    "yugiohmemes",
    "YuGiOhMemes",
    "yugioh",
    "masterduel",
    "duellinks"
]

# =========================
# 🎴 CARTE YU-GI-OH API
# =========================
def get_random_card():
    try:
        url = "https://db.ygoprodeck.com/api/v7/randomcard.php"
        res = requests.get(url, timeout=10)
        data = res.json()

        name = data.get("name", "Carte inconnue")
        desc = data.get("desc", "Pas d'effet")
        image = data["card_images"][0]["image_url"]

        return {
            "name": name,
            "desc": desc[:300] + "...",
            "image": image
        }

    except Exception as e:
        print("❌ Erreur carte:", e)
        return None


# =========================
# 😂 MEME REDDIT AMÉLIORÉ
# =========================
def get_meme():
    try:
        subreddit = random.choice(SUBREDDITS)
        feed_type = random.choice(["new", "hot", "top"])
        after = random.randint(1, 1000)

        url = f"https://www.reddit.com/r/{subreddit}/{feed_type}.json?limit=100&after=t3_{after}"

        headers = {
            "User-Agent": f"DiscordBot:{random.randint(1,999999)}"
        }

        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        posts = data["data"]["children"]
        images = []

        for p in posts:
            post = p["data"]
            url = post.get("url", "")

            if any(url.endswith(ext) for ext in [".jpg", ".png", ".jpeg", ".gif"]):
                images.append(url)

        print(f"📸 {subreddit} ({feed_type}) → {len(images)} images")

        if not images:
            return "https://i.imgur.com/3ZUrjUP.jpeg"

        random.shuffle(images)

        for img in images:
            if img not in sent_memes:
                sent_memes.add(img)

                if len(sent_memes) > 300:
                    sent_memes.clear()

                return img

        print("♻️ Reset memes")
        sent_memes.clear()
        return random.choice(images)

    except Exception as e:
        print("❌ Erreur meme:", e)
        return "https://i.imgur.com/3ZUrjUP.jpeg"


# =========================
# 🎨 EMBED COMBINÉ
# =========================
def create_embed(meme_url, card):
    messages = [
        "⚡ Invocation spéciale !",
        "🔥 Combo ultime activé !",
        "🎴 Duel + meme en cours !",
        "💥 Attaque directe avec un meme !",
        "😂 Piège activé : humour !"
    ]

    embed = discord.Embed(
        title=random.choice(messages),
        color=discord.Color.random()
    )

    # meme
    embed.set_image(url=meme_url)

    # carte
    if card:
        embed.add_field(
            name=f"🎴 {card['name']}",
            value=card["desc"],
            inline=False
        )
        embed.set_thumbnail(url=card["image"])

    embed.set_footer(text=f"📊 Memes envoyés : {meme_stats['sent']}")

    return embed


# =========================
# 🚚 ENVOI
# =========================
async def send_combo(channel):
    meme = get_meme()
    card = get_random_card()

    meme_stats["sent"] += 1

    embed = create_embed(meme, card)
    await channel.send(embed=embed)


# =========================
# 🚀 BOT READY
# =========================
@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")

    await tree.sync()

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Salon introuvable")
        return

    while True:
        await send_combo(channel)
        await asyncio.sleep(1800)  # 30 min


# =========================
# 💬 COMMANDES
# =========================
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "!meme":
        await send_combo(message.channel)

    if message.content == "!card":
        card = get_random_card()
        embed = create_embed("https://i.imgur.com/3ZUrjUP.jpeg", card)
        await message.channel.send(embed=embed)


@tree.command(name="meme", description="Meme + carte Yu-Gi-Oh")
async def meme_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    await send_combo(interaction.channel)


@tree.command(name="card", description="Carte Yu-Gi-Oh aléatoire")
async def card_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    card = get_random_card()
    embed = create_embed("https://i.imgur.com/3ZUrjUP.jpeg", card)
    await interaction.followup.send(embed=embed)


client.run(TOKEN)
