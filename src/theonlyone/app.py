import discord
from discord.ext import commands
import os

# Define as intenções que o bot utilizará para receber eventos do Discord.
# A intenção message_content é necessária para o bot ler o conteúdo das mensagens.
intents = discord.Intents.default()
intents.message_content = True

# Carrega as variáveis de ambiente do arquivo .env para obter o token secreto.
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("TOKEN")

class App(commands.Bot):
    """Classe principal do bot, responsável por inicializar e carregar os comandos."""

    def __init__(self):
        super().__init__(command_prefix=['$', '!'], intents=intents)

    async def setup_hook(self):
        # Monta o caminho até a pasta de comandos e carrega cada extensão Python.
        caminho_atual = os.path.dirname(os.path.abspath(__file__))
        pasta_commands = os.path.join(caminho_atual, 'commands')

        for filename in os.listdir(pasta_commands):
            if filename.endswith(".py"):
                await self.load_extension(f'commands.{filename[:-3]}')
                print(f"Comando {filename} carregado!")

# Instancia o bot e inicia sua execução.
bot = App()

@bot.event
async def on_ready():
    # Evento chamado quando o bot se conecta com sucesso ao Discord.
    print(f"BOT {bot.user} está rodando!")

bot.run(token)
