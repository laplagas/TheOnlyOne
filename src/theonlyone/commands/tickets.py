from discord import app_commands
from discord.ext import commands
import discord
import datetime
from theonlyone.utils.logger import logger


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = {}  # {ticket_id: {"user": user_id, "created_at": timestamp}}
        self.ticket_counter = 0

    # Comando para criar painel de tickets
    @app_commands.command(name="ticket_panel", description="Cria um painel para abrir tickets")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_panel(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
    ):
        """Cria um painel de botão para abrir tickets"""
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="📋 Sistema de Tickets",
            description="Clique no botão abaixo para abrir um ticket e falar com nossos moderadores!",
            color=discord.Color.purple()
        )

        view = TicketView(self.bot, self)
        msg = await canal.send(embed=embed, view=view)

        await interaction.followup.send(
            f"✅ Painel de tickets criado em {canal.mention}",
            ephemeral=True
        )

        logger.info(
            f"Ticket Panel Created | Canal: {canal.name} | Criador: {interaction.user}"
        )

    # Comando para fechar um ticket (uso interno)
    @app_commands.command(name="ticket_close", description="Fecha um ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_close(
        self,
        interaction: discord.Interaction,
        motivo: str = "Ticket encerrado",
    ):
        """Fecha o ticket do canal atual"""
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        if not channel.name.startswith("ticket-"):
            await interaction.followup.send("❌ Este não é um canal de ticket.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔒 Ticket Fechado",
            description=f"Motivo: {motivo}\nFechado por: {interaction.user}",
            color=discord.Color.red()
        )

        await channel.send(embed=embed)
        await interaction.followup.send("✅ Ticket será deletado em 5 segundos...", ephemeral=True)

        # Aguarda e deleta o canal
        await interaction.followup.send(content=".")
        await channel.delete(reason=motivo)

        logger.info(
            f"Ticket Closed | Canal: {channel.name} | Motivo: {motivo} | Fechado por: {interaction.user}"
        )

    # Comando para adicionar membro ao ticket
    @app_commands.command(name="ticket_add", description="Adiciona um membro ao ticket")
    async def ticket_add(
        self,
        interaction: discord.Interaction,
        membro: discord.Member,
    ):
        """Adiciona um membro ao ticket"""
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        if not channel.name.startswith("ticket-"):
            await interaction.followup.send("❌ Este não é um canal de ticket.", ephemeral=True)
            return

        await channel.set_permissions(membro, view_channel=True, send_messages=True)
        await interaction.followup.send(f"✅ {membro.mention} foi adicionado ao ticket.", ephemeral=True)

        logger.info(
            f"Ticket Member Added | Ticket: {channel.name} | Membro: {membro} | Adicionado por: {interaction.user}"
        )

    # Comando para remover membro do ticket
    @app_commands.command(name="ticket_remove", description="Remove um membro do ticket")
    async def ticket_remove(
        self,
        interaction: discord.Interaction,
        membro: discord.Member,
    ):
        """Remove um membro do ticket"""
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        if not channel.name.startswith("ticket-"):
            await interaction.followup.send("❌ Este não é um canal de ticket.", ephemeral=True)
            return

        await channel.set_permissions(membro, view_channel=False, send_messages=False)
        await interaction.followup.send(f"✅ {membro.mention} foi removido do ticket.", ephemeral=True)

        logger.info(
            f"Ticket Member Removed | Ticket: {channel.name} | Membro: {membro} | Removido por: {interaction.user}"
        )


class TicketView(discord.ui.View):
    def __init__(self, bot, cog):
        super().__init__(timeout=None)
        self.bot = bot
        self.cog = cog

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.primary, emoji="📝")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        # Incrementa contador
        self.cog.ticket_counter += 1
        ticket_id = self.cog.ticket_counter

        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")

        # Cria categoria se não existir
        if not category:
            category = await guild.create_category("Tickets")

        # Cria canal de ticket
        ticket_channel = await category.create_text_channel(
            name=f"ticket-{ticket_id}",
            topic=f"Ticket de {interaction.user} | ID: {ticket_id}"
        )

        # Define permissões
        await ticket_channel.set_permissions(guild.default_role, view_channel=False)
        await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)

        # Envia mensagem no ticket
        embed = discord.Embed(
            title=f"Ticket #{ticket_id}",
            description=f"Olá {interaction.user.mention}!\nDescreva seu problema ou dúvida aqui.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Use `/ticket_add` para adicionar moderadores")

        close_view = discord.ui.View()
        close_button = discord.ui.Button(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒")

        async def close_callback(ctx_button: discord.Interaction):
            await ticket_channel.delete(reason=f"Fechado por {ctx_button.user}")

        close_button.callback = close_callback
        close_view.add_item(close_button)

        await ticket_channel.send(embed=embed, view=close_view)

        # Log e armazena
        self.cog.tickets[ticket_id] = {
            "user": interaction.user.id,
            "created_at": datetime.datetime.now(),
            "channel_id": ticket_channel.id
        }

        await interaction.followup.send(
            f"✅ Ticket criado! {ticket_channel.mention}",
            ephemeral=True
        )

        logger.info(
            f"Ticket Created | ID: {ticket_id} | Usuário: {interaction.user} | "
            f"Canal: {ticket_channel.name}"
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
