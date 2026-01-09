import os
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

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant.")
if CHANNEL_ID == 0:
    raise RuntimeError("CHANNEL_ID manquant.")

INTENTS = discord.Intents.default()
INTENTS.message_content = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=INTENTS)

    async def setup_hook(self):
        await self.tree.sync()

bot = Bot()

def allowed_channel(interaction: discord.Interaction) -> bool:
    return interaction.channel is not None and interaction.channel.id == CHANNEL_ID

@bot.event
async def on_ready():
    print(f"✅ Connecté: {bot.user} (id={bot.user.id})")

@bot.tree.command(name="health", description="Vérifie que le bot fonctionne.")
async def health(interaction: discord.Interaction):
    if not allowed_channel(interaction):
        await interaction.response.send_message("Ce bot ne fonctionne que dans son salon dédié 😉", ephemeral=True)
        return
    await interaction.response.send_message("✅ Je suis en ligne !")

bot.run(DISCORD_TOKEN)
