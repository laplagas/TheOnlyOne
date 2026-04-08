import discord
from discord.ext import commands
import os
import sys

# Garante que a pasta src/ esteja no caminho de importação
package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

# Define as intenções que o bot utilizará para receber eventos do Discord.
# A intenção message_content é necessária para o bot ler o conteúdo das mensagens.
intents = discord.Intents.default()
intents.message_content = True

# Carrega as variáveis de ambiente do arquivo .env para obter o token secreto.
from dotenv import load_dotenv
load_dotenv()

Token = os.getenv("TOKEN")
if not Token:
    raise RuntimeError(
        "TOKEN não encontrado. Crie um arquivo .env com TOKEN=seu_token ou defina a variável de ambiente TOKEN."
    )

class App(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=['$', '!'],
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        caminho_atual = os.path.dirname(os.path.abspath(__file__))
        pasta_commands = os.path.join(caminho_atual, 'commands')

        for filename in os.listdir(pasta_commands):
            if filename.endswith(".py") and filename != "__init__.py":
                await self.load_extension(f'theonlyone.commands.{filename[:-3]}')
                print(f"Comando {filename} carregado!")

        await self.tree.sync()


bot = App()

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Protegendo o servidor 🛡️"
        )
    )

    print(f"BOT {bot.user} está rodando!")

if __name__ == "__main__":
    bot.run(Token)
    