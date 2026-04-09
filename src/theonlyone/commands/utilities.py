import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
import datetime
from theonlyone.utils.logger import logger
from collections import defaultdict
import asyncio


class ReminderModal(ui.Modal, title="Criar Lembrete"):
    """Modal para criar um lembrete"""
    
    titulo = ui.TextInput(
        label="Título do Lembrete",
        placeholder="Ex: Reunião com o time",
        max_length=100,
    )
    
    mensagem = ui.TextInput(
        label="Mensagem",
        placeholder="Descrição do lembrete",
        style=discord.TextStyle.paragraph,
        max_length=500,
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Lembrete Criado",
            description=f"**{self.titulo.value}**\n\n{self.mensagem.value}",
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class EmbedCustomizerModal(ui.Modal, title="Customizar Embed"):
    """Modal para criar embeds customizados"""
    
    titulo = ui.TextInput(
        label="Título",
        placeholder="Título do embed",
        max_length=256,
    )
    
    descricao = ui.TextInput(
        label="Descrição",
        placeholder="Descrição do embed",
        style=discord.TextStyle.paragraph,
        max_length=4000,
    )
    
    cor = ui.TextInput(
        label="Cor (Hex)",
        placeholder="Ex: FF5733 (deixe em branco para azul padrão)",
        max_length=6,
        required=False,
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            color_value = self.cor.value if self.cor.value else "0099FF"
            color = discord.Color(int(color_value, 16))
        except ValueError:
            await interaction.response.send_message(
                "❌ Cor inválida. Use formato Hex (ex: FF5733)",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=self.titulo.value,
            description=self.descricao.value,
            color=color,
        )
        embed.set_footer(text=f"Customizado por {interaction.user}")
        
        await interaction.response.send_message(
            "✅ Embed criado! Aqui está a preview:",
            embed=embed,
            ephemeral=True
        )


class EmbedTemplatesView(ui.View):
    """Select Menu para escolher templates de embed"""
    
    def __init__(self):
        super().__init__()
        self.selected_template = None
    
    @ui.select(
        placeholder="Escolha um template de embed",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Aviso",
                value="aviso",
                description="Template para avisos",
                emoji="⚠️"
            ),
            discord.SelectOption(
                label="Sucesso",
                value="sucesso",
                description="Template para confirmação",
                emoji="✅"
            ),
            discord.SelectOption(
                label="Erro",
                value="erro",
                description="Template para erros",
                emoji="❌"
            ),
            discord.SelectOption(
                label="Informação",
                value="info",
                description="Template para informações",
                emoji="ℹ️"
            ),
            discord.SelectOption(
                label="Anúncio",
                value="anuncio",
                description="Template para anúncios",
                emoji="📢"
            ),
        ]
    )
    async def select_template(self, interaction: discord.Interaction, select: ui.Select):
        self.selected_template = select.values[0]
        
        templates = {
            "aviso": {
                "color": discord.Color.orange(),
                "title": "⚠️ Aviso",
                "description": "Adicione sua mensagem aqui",
            },
            "sucesso": {
                "color": discord.Color.green(),
                "title": "✅ Sucesso",
                "description": "Operação concluída com sucesso!",
            },
            "erro": {
                "color": discord.Color.red(),
                "title": "❌ Erro",
                "description": "Ocorreu um erro. Tente novamente.",
            },
            "info": {
                "color": discord.Color.blue(),
                "title": "ℹ️ Informação",
                "description": "Informação importante.",
            },
            "anuncio": {
                "color": discord.Color.purple(),
                "title": "📢 Anúncio",
                "description": "Novo anúncio do servidor!",
            },
        }
        
        template = templates[self.selected_template]
        embed = discord.Embed(
            title=template["title"],
            description=template["description"],
            color=template["color"],
        )
        
        await interaction.response.send_message(
            f"✅ Template **{self.selected_template.capitalize()}** selecionado!",
            embed=embed,
            ephemeral=True
        )
        self.stop()


class Utilities(commands.Cog):
    """Cog para utilitários: lembretes, eventos e embeds customizados"""
    
    def __init__(self, bot):
        self.bot = bot
        self.reminders = defaultdict(list)  # {user_id: [{"titulo": str, "mensagem": str, "tempo": datetime}]}
        self.events = defaultdict(list)  # {guild_id: [{"nome": str, "data": str, "hora": str}]}
        self.custom_embeds = defaultdict(dict)  # {guild_id: {nome: embed_dict}}
        self.check_reminders.start()

    # ==================== REMINDER ====================
    @app_commands.command(name="reminder", description="Criar um lembrete")
    async def reminder(self, interaction: discord.Interaction):
        """Abre modal para criar um lembrete"""
        await interaction.response.send_modal(ReminderModal())
        logger.info(f"Modal de lembrete aberto | Usuário: {interaction.user}")

    @app_commands.command(name="reminders", description="Ver seus lembretes")
    async def reminders(self, interaction: discord.Interaction):
        """Exibe todos os lembretes do usuário"""
        user_id = interaction.user.id
        
        if user_id not in self.reminders or not self.reminders[user_id]:
            embed = discord.Embed(
                title="✅ Sem Lembretes",
                description="Você não possui lembretes. Use `/reminder` para criar um!",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"⏰ Seus Lembretes ({len(self.reminders[user_id])})",
            color=discord.Color.blue(),
        )
        
        for i, reminder in enumerate(self.reminders[user_id], 1):
            embed.add_field(
                name=f"{i}. {reminder['titulo']}",
                value=f"{reminder['mensagem']}\n**Criado em:** {reminder['criado_em'].strftime('%d/%m/%Y %H:%M')}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ==================== EVENT ====================
    @app_commands.command(name="event", description="Criar um evento")
    async def event(
        self,
        interaction: discord.Interaction,
        nome: str,
        data: str,
        hora: str,
    ):
        """Cria um evento para o servidor
        Formato de data: DD/MM/YYYY
        Formato de hora: HH:MM
        """
        guild_id = interaction.guild.id
        
        try:
            # Validar formato
            datetime.datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M")
        except ValueError:
            embed = discord.Embed(
                title="❌ Formato Inválido",
                description="Use:\n**Data:** DD/MM/YYYY\n**Hora:** HH:MM",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        event_data = {
            "nome": nome,
            "data": data,
            "hora": hora,
            "criador": interaction.user.mention,
            "criado_em": datetime.datetime.now(),
        }
        
        self.events[guild_id].append(event_data)
        
        embed = discord.Embed(
            title="📅 Evento Criado",
            description=f"**Nome:** {nome}\n**Data:** {data}\n**Hora:** {hora}",
            color=discord.Color.purple(),
        )
        embed.set_footer(text=f"Criado por {interaction.user}")
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Evento criado | Servidor: {interaction.guild.name} | Evento: {nome}")

    @app_commands.command(name="events", description="Ver eventos do servidor")
    async def events(self, interaction: discord.Interaction):
        """Exibe todos os eventos do servidor"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.events or not self.events[guild_id]:
            embed = discord.Embed(
                title="✅ Sem Eventos",
                description="Não há eventos agendados. Use `/event` para criar um!",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📅 Eventos do Servidor ({len(self.events[guild_id])})",
            color=discord.Color.purple(),
        )
        
        for i, event in enumerate(self.events[guild_id], 1):
            embed.add_field(
                name=f"{i}. {event['nome']}",
                value=f"📅 {event['data']} às {event['hora']}\nCriado por: {event['criador']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ==================== EMBED CUSTOMIZER ====================
    @app_commands.command(name="embed", description="Criar um embed customizado")
    async def embed_create(self, interaction: discord.Interaction):
        """Abre modal para criar um embed customizado"""
        await interaction.response.send_modal(EmbedCustomizerModal())
        logger.info(f"Modal de embed aberto | Usuário: {interaction.user}")

    @app_commands.command(name="embed_templates", description="Ver templates de embeds")
    async def embed_templates(self, interaction: discord.Interaction):
        """Mostra templates pré-definidos de embeds"""
        embed = discord.Embed(
            title="🎨 Templates de Embed",
            description="Escolha um template abaixo:",
            color=discord.Color.blurple(),
        )
        
        view = EmbedTemplatesView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        logger.info(f"Templates de embed mostrados | Usuário: {interaction.user}")

    @app_commands.command(name="embed_list", description="Listar embeds customizados salvos")
    async def embed_list(self, interaction: discord.Interaction):
        """Lista todos os embeds customizados do servidor"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.custom_embeds or not self.custom_embeds[guild_id]:
            embed = discord.Embed(
                title="✅ Sem Embeds Salvos",
                description="Nenhum embed customizado salvo. Use `/embed` para criar um!",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🎨 Embeds Customizados ({len(self.custom_embeds[guild_id])})",
            color=discord.Color.blurple(),
        )
        
        for nome in self.custom_embeds[guild_id]:
            embed.add_field(name=nome, value="✅ Salvo", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ==================== BACKGROUND TASK ====================
    @tasks.loop(minutes=1)
    async def check_reminders(self):
        """Verifica lembretes a cada minuto (placeholder para demo)"""
        # Implementação completa de notificações seria com persistência em BD
        pass

    @check_reminders.before_loop
    async def before_check_reminders(self):
        """Aguarda o bot estar pronto antes de iniciar a task"""
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Utilities(bot))
