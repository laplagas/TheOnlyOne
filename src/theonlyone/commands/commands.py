import discord
from discord.ext import commands
import datetime
from theonlyone.utils.logger import logger


class Cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}  # Dicionário simples para avisos (temporário, em memória)

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

    # Comando para kick (expulsar)
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, membro: discord.Member, *, motivo="Não informado!"):
        await membro.kick(reason=motivo)

        await ctx.send(f"👢 {membro.mention} foi expulso com sucesso!")

        logger.info(
            f"Kick | Usuário: {membro} | ID: {membro.id} | "
            f"Servidor: {ctx.guild.name} | Moderador: {ctx.author} | "
            f"Horário: {datetime.datetime.now()}"
        )

    # Comando para warn (aviso)
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, membro: discord.Member, *, motivo="Não informado!"):
        user_id = str(membro.id)
        if user_id not in self.warns:
            self.warns[user_id] = []
        self.warns[user_id].append({"motivo": motivo, "moderador": str(ctx.author), "data": datetime.datetime.now()})

        count = len(self.warns[user_id])
        await ctx.send(f"⚠️ {membro.mention} recebeu um aviso ({count} total).\nMotivo: {motivo}")

        logger.info(
            f"Warn | Usuário: {membro} | Moderador: {ctx.author} | Motivo: {motivo}"
        )

    # Comando para ver warns
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, membro: discord.Member):
        user_id = str(membro.id)
        if user_id not in self.warns or not self.warns[user_id]:
            await ctx.send(f"✅ {membro.mention} não tem avisos.")
            return

        embed = discord.Embed(title=f"Avisos de {membro}", color=discord.Color.orange())
        for i, w in enumerate(self.warns[user_id], 1):
            embed.add_field(name=f"Aviso {i}", value=f"Motivo: {w['motivo']}\nModerador: {w['moderador']}\nData: {w['data']}", inline=False)
        await ctx.send(embed=embed)

    # Comando para mute (silenciar)
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, membro: discord.Member, *, motivo="Não informado!"):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted", color=discord.Color.dark_gray())
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)

        await membro.add_roles(muted_role, reason=motivo)
        await ctx.send(f"🔇 {membro.mention} foi silenciado.\nMotivo: {motivo}")

        logger.info(
            f"Mute | Usuário: {membro} | Moderador: {ctx.author} | Motivo: {motivo}"
        )

    # Comando para unmute
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, membro: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role and muted_role in membro.roles:
            await membro.remove_roles(muted_role)
            await ctx.send(f"🔊 {membro.mention} foi dessilenciado.")
            logger.info(f"Unmute | Usuário: {membro} | Moderador: {ctx.author}")
        else:
            await ctx.send("❌ Usuário não está silenciado.")

    # Comando para info do usuário
    @commands.command()
    async def userinfo(self, ctx, membro: discord.Member = None):
        membro = membro or ctx.author
        embed = discord.Embed(title=f"Info de {membro}", color=membro.color)
        embed.add_field(name="ID", value=membro.id, inline=True)
        embed.add_field(name="Entrou em", value=membro.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Conta criada", value=membro.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Roles", value=", ".join([r.name for r in membro.roles[1:]]), inline=False)
        embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
        await ctx.send(embed=embed)

    # Comando para info do servidor
    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"Info do {guild.name}", color=discord.Color.blue())
        embed.add_field(name="Membros", value=guild.member_count, inline=True)
        embed.add_field(name="Canais", value=len(guild.channels), inline=True)
        embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        await ctx.send(embed=embed)

    # Comando de ajuda
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Comandos do Bot", description="Prefixos: $ ou !", color=discord.Color.green())
        embed.add_field(name="Moderação", value="`ban`, `unban`, `kick`, `timeout`, `clear`, `warn`, `warnings`, `mute`, `unmute`", inline=False)
        embed.add_field(name="Utilitários", value="`ping`, `userinfo`, `serverinfo`", inline=False)
        await ctx.send(embed=embed)

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