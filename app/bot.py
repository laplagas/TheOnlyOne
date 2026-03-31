import discord
from discord.ext import commands
import asyncio
import os
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=['$', '!'], intents=intents)
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("TOKEN")
print(f"token carregado: {token}")
@bot.event
async def on_ready():
    print(f'''BOT WORKING:
          {bot.user}
          {bot.guilds}''')
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong🏓 {round(bot.latency * 1000)}ms")
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, membro: discord.Member, *, motivo="Não informado!"):
    mod = ctx.author
    await membro.ban(reason=motivo)
    await ctx.send(f"Membro {membro.mention} foi banido com sucesso!")
    print(f"Usuario: {membro.name}\n id: {membro.id}\n Foi banido do servidor: {ctx.guild.name}\n Moderador: {mod}")

@ban.error
async def bot_erro(ctx,erro):
    if isinstance(erro, commands.MissingPermissions):
        await ctx.send("Você não tem permissão pra realziar está ação!")
    elif isinstance(erro, commands.BotMissingPermissions):
        await ctx.send(f"**{bot.user} não tem permissão pra fazer isso!**")
    else:
        print(erro)

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, membro: discord.User):
    mod = ctx.author
    try:
        await ctx.guild.unban(membro)
        await ctx.send(f"Usuario {membro} foi desbanido com sucesso!")
        print(f"Usuario: {membro.name} foi desbanido do servidor {ctx.guild.name}")
    except discord.NotFound:
        await ctx.send(f"{membro} não foi banido do servidor!")
        print(f"Moderador {mod} tentou desbanir um usuario não banido.")
    except Exception as e:
        await ctx.send(f"Ocorreu um erro: {e}")
        print(f"Ocorreu um erro: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx,msg: int):
    mod = ctx.author
    apagar = await ctx.channel.purge(limit=msg + 1)
    await asyncio.sleep(2)
    await ctx.send(f'{msg} mensagens apagadas, do canal {ctx.channel}!', delete_after=5)
    print(f"{mod} apagou {msg} mensagens no canal {ctx.channel}!")
@clear.error
async def bot_error(ctx,error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**Você não tem permissão para realizar está operação!❌**")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"**{bot.user} não tem permissão pra realizar está ação!❌**")
    else:
        print(error)
bot.run(token)