from discord import app_commands
from discord.ext import commands
import discord
import datetime
from theonlyone.utils.logger import logger


class CmdSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}  # Dicionário simples para avisos (temporário, em memória)

    # Comando simples para verificar latência
    @app_commands.command(name="ping", description="Latência do bot")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! {latency}ms")

    # Comando para banir um usuário
    @app_commands.command(name="ban", description="Banir um usuário")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        motivo: str = "Não informado!",
    ):
        await user.ban(reason=motivo)

        await interaction.response.send_message(
            f"🔨 {user.mention} foi banido.\n"
            f"Motivo: {motivo}\n"
            f"Responsável: {interaction.user}"
        )

        logger.info(
            f"Ban | Usuário: {user} | ID: {user.id} | "
            f"Servidor: {interaction.guild.name} | Moderador: {interaction.user}"
        )

    # Comando de timeout com escolha de unidade de tempo
    @app_commands.command(name="timeout", description="Aplicar timeout em um membro")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.choices(
        unidade=[
            app_commands.Choice(name="Segundos", value="s"),
            app_commands.Choice(name="Minutos", value="m"),
            app_commands.Choice(name="Horas", value="h"),
            app_commands.Choice(name="Dias", value="d"),
        ]
    )
    async def timeout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        tempo: int,
        unidade: app_commands.Choice[str],
        motivo: str = "Não informado!",
    ):
        if tempo <= 0:
            return await interaction.response.send_message(
                "❌ Tempo inválido.",
                ephemeral=True
            )

        mapa_tempo = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
        }

        delta = datetime.timedelta(**{mapa_tempo[unidade.value]: tempo})
        duracao = discord.utils.utcnow() + delta

        await user.timeout(duracao, reason=motivo)

        await interaction.response.send_message(
            f"⏳ {user.mention} ficou em timeout por {tempo}{unidade.value}\n"
            f"Motivo: {motivo}\n"
            f"Responsável: {interaction.user}"
        )

        logger.info(
            f"Timeout | Usuário: {user} | Tempo: {tempo}{unidade.value} | "
            f"Servidor: {interaction.guild.name} | Moderador: {interaction.user}"
        )
        
        # Comando para limpar chats
    @app_commands.command(
    name="clear",
    description="Limpa mensagens do chat (máx: 1000)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        quantidade: int
    ):
        # validação
        if quantidade <= 0 or quantidade > 1000:
            return await interaction.response.send_message(
                f"⚠️ Quantidade inválida: {quantidade} (use 1–1000).",
                ephemeral=True
            )

        # evita timeout da interação
        await interaction.response.defer(ephemeral=True)

        # remove mensagens (+1 para apagar o comando)
        deletadas = await interaction.channel.purge(limit=quantidade + 1)

        # resposta final
        await interaction.followup.send(
            f"🧹 {len(deletadas) - 1} mensagens foram apagadas.",
            ephemeral=True
        )

        # log estruturado
        logger.info(
            f"Clear | Autor: {interaction.user} | "
            f"Canal: {interaction.channel} | Quantidade: {quantidade}"
        )

    # Comando para kick
    @app_commands.command(name="kick", description="Expulsar um membro")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        motivo: str = "Não informado!",
    ):
        await user.kick(reason=motivo)

        await interaction.response.send_message(
            f"👢 {user.mention} foi expulso.\nMotivo: {motivo}\nResponsável: {interaction.user}"
        )

        logger.info(
            f"Kick | Usuário: {user} | ID: {user.id} | "
            f"Servidor: {interaction.guild.name} | Moderador: {interaction.user}"
        )

    # Comando para warn
    @app_commands.command(name="warn", description="Dar aviso a um membro")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        motivo: str = "Não informado!",
    ):
        user_id = str(user.id)
        if user_id not in self.warns:
            self.warns[user_id] = []
        self.warns[user_id].append({"motivo": motivo, "moderador": str(interaction.user), "data": datetime.datetime.now()})

        count = len(self.warns[user_id])
        await interaction.response.send_message(
            f"⚠️ {user.mention} recebeu um aviso ({count} total).\nMotivo: {motivo}\nResponsável: {interaction.user}"
        )

        logger.info(
            f"Warn | Usuário: {user} | Moderador: {interaction.user} | Motivo: {motivo}"
        )

    # Comando para ver warnings
    @app_commands.command(name="warnings", description="Ver avisos de um membro")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warnings(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        user_id = str(user.id)
        if user_id not in self.warns or not self.warns[user_id]:
            await interaction.response.send_message(f"✅ {user.mention} não tem avisos.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Avisos de {user}", color=discord.Color.orange())
        for i, w in enumerate(self.warns[user_id], 1):
            embed.add_field(name=f"Aviso {i}", value=f"Motivo: {w['motivo']}\nModerador: {w['moderador']}\nData: {w['data']}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Comando para mute
    @app_commands.command(name="mute", description="Silenciar um membro")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        motivo: str = "Não informado!",
    ):
        await interaction.response.defer(ephemeral=True)

        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="Muted", color=discord.Color.dark_gray())
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)

        await user.add_roles(muted_role, reason=motivo)
        await interaction.followup.send(
            f"🔇 {user.mention} foi silenciado.\nMotivo: {motivo}\nResponsável: {interaction.user}"
        )

        logger.info(
            f"Mute | Usuário: {user} | Moderador: {interaction.user} | Motivo: {motivo}"
        )

    # Comando para unmute
    @app_commands.command(name="unmute", description="Dessilenciar um membro")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unmute(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if muted_role and muted_role in user.roles:
            await user.remove_roles(muted_role)
            await interaction.response.send_message(f"🔊 {user.mention} foi dessilenciado.")
            logger.info(f"Unmute | Usuário: {user} | Moderador: {interaction.user}")
        else:
            await interaction.response.send_message("❌ Usuário não está silenciado.", ephemeral=True)

    # Comando para userinfo
    @app_commands.command(name="userinfo", description="Info de um usuário")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None,
    ):
        user = user or interaction.user
        embed = discord.Embed(title=f"Info de {user}", color=user.color)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Entrou em", value=user.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Conta criada", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Roles", value=", ".join([r.name for r in user.roles[1:]]), inline=False)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        await interaction.response.send_message(embed=embed)

    # Comando para serverinfo
    @app_commands.command(name="serverinfo", description="Info do servidor")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"Info do {guild.name}", color=discord.Color.blue())
        embed.add_field(name="Membros", value=guild.member_count, inline=True)
        embed.add_field(name="Canais", value=len(guild.channels), inline=True)
        embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        await interaction.response.send_message(embed=embed)

    # Comando de help
    @app_commands.command(name="help", description="Lista de comandos")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Comandos do Bot", description="Use / para slash commands ou $ / ! para prefixados", color=discord.Color.green())
        embed.add_field(name="Moderação", value="ban, unban, kick, timeout, clear, warn, warnings, mute, unmute", inline=False)
        embed.add_field(name="Utilitários", value="ping, userinfo, serverinfo", inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(CmdSlash(bot))