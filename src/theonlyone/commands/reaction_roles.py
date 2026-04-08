from discord import app_commands
from discord.ext import commands
import discord
from theonlyone.utils.logger import logger


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_roles = {}  # {message_id: {emoji: role_id}}

    # Comando para criar reaction role
    @app_commands.command(name="reaction_role_setup", description="Configura um sistema de reaction role")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reaction_role_setup(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        titulo: str,
        descricao: str,
    ):
        """Cria uma mensagem com reações para dar roles aos membros"""
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Reaja com um emoji para receber a role correspondente")

        msg = await canal.send(embed=embed)
        self.reaction_roles[msg.id] = {}

        await interaction.followup.send(
            f"✅ Mensagem de reaction role criada em {canal.mention}\n"
            f"**ID da mensagem:** {msg.id}\n"
            f"Use `/reaction_role_add` para adicionar emojis e roles",
            ephemeral=True
        )

        logger.info(
            f"Reaction Role Setup | Canal: {canal} | "
            f"Mensagem ID: {msg.id} | Criador: {interaction.user}"
        )

    # Comando para adicionar emoji e role
    @app_commands.command(name="reaction_role_add", description="Adiciona um emoji e uma role")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reaction_role_add(
        self,
        interaction: discord.Interaction,
        message_id: int,
        emoji: str,
        role: discord.Role,
    ):
        """Adiciona um emoji e uma role associada a uma mensagem"""
        await interaction.response.defer(ephemeral=True)

        if message_id not in self.reaction_roles:
            await interaction.followup.send("❌ Mensagem não encontrada. Use `/reaction_role_setup` primeiro.", ephemeral=True)
            return

        self.reaction_roles[message_id][emoji] = role.id

        # Tenta reagir com o emoji
        try:
            msg_obj = await interaction.channel.fetch_message(message_id)
            await msg_obj.add_reaction(emoji)
        except discord.NotFound:
            await interaction.followup.send("❌ Mensagem não encontrada neste canal.", ephemeral=True)
            return
        except discord.HTTPException:
            await interaction.followup.send("⚠️ Erro ao reagir. Emoji válido?", ephemeral=True)
            return

        await interaction.followup.send(
            f"✅ {emoji} → {role.mention} adicionado com sucesso!",
            ephemeral=True
        )

        logger.info(
            f"Reaction Role Add | Emoji: {emoji} | Role: {role.name} | "
            f"Mensagem ID: {message_id} | Criador: {interaction.user}"
        )

    # Listener para reações adicionadas
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in self.reaction_roles:
            return

        emoji_str = str(payload.emoji)
        if emoji_str not in self.reaction_roles[payload.message_id]:
            return

        role_id = self.reaction_roles[payload.message_id][emoji_str]
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)

        if role and member:
            try:
                await member.add_roles(role)
                logger.info(f"Reaction Role | {member} recebeu {role.name}")
            except discord.Forbidden:
                logger.error(f"Sem permissão para dar role {role.name}")

    # Listener para reações removidas
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in self.reaction_roles:
            return

        emoji_str = str(payload.emoji)
        if emoji_str not in self.reaction_roles[payload.message_id]:
            return

        role_id = self.reaction_roles[payload.message_id][emoji_str]
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)

        if role and member:
            try:
                await member.remove_roles(role)
                logger.info(f"Reaction Role Removed | {member} perdeu {role.name}")
            except discord.Forbidden:
                logger.error(f"Sem permissão para remover role {role.name}")


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
