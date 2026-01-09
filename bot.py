import os
import time
import random
import discord
from discord import app_commands
from discord.ext import commands

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
TZ = os.getenv("TZ", "Europe/Paris")  # juste pour cohérence Railway

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant.")
if CHANNEL_ID == 0:
    raise RuntimeError("CHANNEL_ID manquant (id du salon #😂・memes-ygo).")

INTENTS = discord.Intents.default()
INTENTS.message_content = True  # nécessaire pour lire les messages (triggers)

class MemeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=INTENTS)
        self._last_auto_meme_ts = 0.0  # cooldown global anti-spam

    async def setup_hook(self):
        # Slash commands global
        await self.tree.sync()

bot = MemeBot()

def is_target_channel(channel: discord.abc.GuildChannel | None) -> bool:
    return channel is not None and getattr(channel, "id", None) == CHANNEL_ID

def global_cooldown_ok(now: float, cooldown_s: int = 20) -> bool:
    return (now - bot._last_auto_meme_ts) >= cooldown_s

# --- Events ---
@bot.event
async def on_ready():
    print(f"✅ Le Livreur de Memes connecté : {bot.user} (id={bot.user.id}) | TZ={TZ}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Ignore tout ce qui n'est pas le salon dédié
    if not is_target_channel(message.channel):
        return

    content = (message.content or "").lower()

    triggers = [
        "brick", "brique", "topdeck", "missplay", "misplay",
        "ash", "maxx", "rng", "chance", "no starter", "starter"
    ]

    if any(t in content for t in triggers):
        now = time.time()
        if global_cooldown_ok(now, cooldown_s=20) and random.random() < 0.35:
            bot._last_auto_meme_ts = now
            replies = [
                "🃏 *Toon World* a détecté un moment légendaire. 😂",
                "Quand tu dis “ça va”, mais ta main dit “non”.",
                "Le duel t’a choisi. Et il t’a choisi pour souffrir (un peu). 😭",
                "Topdeck ? Non. **Top-brique.**",
                "Ash a encore frappé… l’histoire se répète.",
            ]
            await message.channel.send(random.choice(replies))

    await bot.process_commands(message)

# --- Slash commands ---
@bot.tree.command(name="health", description="Vérifie que Le Livreur de Memes fonctionne.")
async def health(interaction: discord.Interaction):
    if not is_target_channel(interaction.channel):
        await interaction.response.send_message(
            "Je fonctionne uniquement dans #😂・memes-ygo 😉",
            ephemeral=True
        )
        return
    await interaction.response.send_message("✅ Le Livreur de Memes est en ligne !")

@bot.tree.command(name="meme", description="Poste un meme (texte) dans #😂・memes-ygo.")
async def meme(interaction: discord.Interaction):
    if not is_target_channel(interaction.channel):
        await interaction.response.send_message(
            "Va dans #😂・memes-ygo pour utiliser /meme 😉",
            ephemeral=True
        )
        return

    memes = [
        "Quand tu gardes une main “acceptable”… et tu pioches encore pire.",
        "‘Je joue autour de tout’ — *se fait punir par la seule carte possible.*",
        "Le plan était parfait… jusqu’à la pioche.",
        "C’est pas un missplay si tu fais semblant d’avoir voulu ça.",
        "Le vrai boss final : **la main de départ**.",
    ]
    await interaction.response.send_message("😂 " + random.choice(memes))

# --- Run ---
bot.run(DISCORD_TOKEN)
