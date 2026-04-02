import discord
from discord.ext import commands
import datetime
from theonlyone.utils.logger import logger


class Cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando para verificar latência
    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! {latency}ms")

    # Comando para banir um membro
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, membro: discord.Member, *, motivo="Não informado!"):
        await membro.ban(reason=motivo)

        await ctx.send(f"🔨 {membro.mention} foi banido com sucesso!")

        logger.info(
            f"Ban | Usuário: {membro} | ID: {membro.id} | "
            f"Servidor: {ctx.guild.name} | Moderador: {ctx.author} | "
            f"Horário: {datetime.datetime.now()}"
        )

    # Comando para desbanir usuário
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, membro: discord.User):
        await ctx.guild.unban(membro)

        await ctx.send(f"✅ Usuário {membro} foi desbanido com sucesso!")

        logger.info(
            f"Unban | Usuário: {membro} | Servidor: {ctx.guild.name} | "
            f"Moderador: {ctx.author} | Horário: {datetime.datetime.now()}"
        )

    # Comando para limpar mensagens
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, quantidade: int):
        if quantidade <= 0 or quantidade > 1000:
            return await ctx.send(
                f"❌ Número inválido. Use entre 1 e 1000 (recebido: {quantidade})."
            )

        await ctx.channel.purge(limit=quantidade + 1)

        await ctx.send(
            f"🧹 {quantidade} mensagens apagadas no canal {ctx.channel}!",
            delete_after=5
        )

        logger.info(
            f"Clear | Moderador: {ctx.author} | Canal: {ctx.channel} | "
            f"Quantidade: {quantidade}"
        )

    # Comando de timeout
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx,
        membro: discord.Member,
        tempo: int,
        unidade: str,
        *,
        motivo="Não informado!",
    ):
        unidade = unidade.lower()

        mapa_tempo = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
        }

        if tempo <= 0:
            return await ctx.send(f"❌ Tempo inválido: {tempo}")

        if unidade not in mapa_tempo:
            return await ctx.send("❌ Use: s (segundos), m, h ou d.")

        delta = datetime.timedelta(**{mapa_tempo[unidade]: tempo})
        duracao = discord.utils.utcnow() + delta

        await membro.timeout(duracao, reason=motivo)

        await ctx.send(
            f"⏳ {membro.mention} ficou em timeout por {tempo}{unidade}\n"
            f"Motivo: {motivo}\n"
            f"Responsável: {ctx.author}"
        )

    # Tratamento global de erros
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para esta ação.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Eu não tenho permissão para executar isso.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Membro não encontrado.")
        else:
            await ctx.send("❌ Ocorreu um erro inesperado.")

            logger.error(
                f"Erro | Servidor: {ctx.guild.name} | "
                f"Horário: {datetime.datetime.now()} | Erro: {error}"
            )


async def setup(bot):
    await bot.add_cog(Cmd(bot))