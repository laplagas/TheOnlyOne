import discord
from discord.ext import commands
import datetime
from theonlyone.utils.logger import logger

# Cog principal que agrupa todos os comandos do bot.
class CMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def ping(self, ctx):
        # Envia uma resposta de latência para confirmar que o bot está online.
        await ctx.send(f"Pong🏓 {round(self.bot.latency * 1000)}ms")
        
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, membro: discord.Member, *, motivo="Não informado!"):
        # Bane o membro especificado e registra o evento no log.
        await membro.ban(reason=motivo)
        await ctx.send(f"Membro {membro.mention} foi banido com sucesso!")
        logger.info(f"Usuario: {membro} | ID: {membro.id} | Servidor: {ctx.guild.name} | Moderador: {ctx.author} | Horario: {datetime.datetime.now()}")
        
        

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, membro: discord.User):
        # Remove o banimento de um usuário previamente banido.
        await ctx.guild.unban(membro)
        await ctx.send(f"Usuario {membro} foi desbanido com sucesso!")
        logger.info(f"Usuario: {membro.name} foi desbanido | Servidor: {ctx.guild.name} | Responsavel: {ctx.author} | Horario: {datetime.datetime.now()}")
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, msg: int):
        # Apaga a quantidade de mensagens solicitada no canal atual.
        if msg > 0 or msg < 1000:
            return await ctx.send(f"Numero de mensagens máxima é 1000 | {msg} é um número invalido")
        await ctx.channel.purge(limit=msg + 1)
        await ctx.send(f'{msg} mensagens apagadas, do canal {ctx.channel}!', delete_after=5)
        logger.info(f"Moderador: {ctx.author} | Canal: {ctx.channel} | Qtd. de msgs: {msg}")
        

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    
    async def timeout(self,ctx,membro: discord.Member,tempo: int, tipotempo,*, motivo = "Não informado!"):
        # Aplica um timeout em um membro com base em duração e tipo de tempo.
        tipotempo = tipotempo.lower()
        tempo_valido = {
            'd' : 'days',
            'h' : 'hours',
            'm' : 'minutes',
            's' : 'seconds'
        }
        if tempo <= 0:
            return await ctx.send(f"**Tempo '{tempo}' invalido**")
        if tipotempo not in tempo_valido:
            return await ctx.send(f"Durações disponiveis: 's/m/h/d'!")
        deltatime = {tempo_valido[tipotempo]: tempo}
        duracao = discord.utils.utcnow() + datetime.timedelta(**deltatime)
        await membro.timeout(duracao, reason=motivo)
        await ctx.send(f"Membro: {membro} | Duração: {tempo} | Motivo: {motivo} | Responsavel: {ctx.author}")

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        # Trata erros comuns de permissão e usuário não encontrado.
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você não tem permisão pra realizar está ação.")
        elif isinstance(error, commands.BotMissingPermissions):
           await ctx.send("Não tenho permisão pra realizar está ação.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Membro não encontrado!")
        else:
            await ctx.send(f"Ocorreu um erro | {error}")
            logger.error(f"Ocorreu um erro em: {ctx.guild.name} | Horario: {datetime.datetime.now()} | Erro: {error}")

# Registra o cog junto ao bot quando a extensão for carregada.
async def setup(bot):
    await bot.add_cog(CMD(bot))