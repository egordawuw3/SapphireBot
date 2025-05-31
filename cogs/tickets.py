import disnake
from disnake.ext import commands
import asyncio
import logging
from utils.embed_utils import make_embed
from config.constants import STAFF_ROLE_ID, INFO_COLOR, ERROR_COLOR, SUCCESS_COLOR

logger = logging.getLogger(__name__)

class TicketModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Тема тикета",
                custom_id="ticket_title",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Описание",
                custom_id="ticket_description",
                style=disnake.TextInputStyle.paragraph
            )
        ]
        super().__init__(
            title="Создать тикет",
            custom_id="ticket_modal",
            components=components
        )

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        try:
            await inter.response.defer(ephemeral=True)
            ticket_number = await self.get_next_ticket_number(inter.guild)
            overwrites = {
                inter.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                inter.user: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
                inter.guild.me: disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            staff_role = inter.guild.get_role(STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            category = disnake.utils.get(inter.guild.categories, name="— × tickets")
            if not category:
                category = await inter.guild.create_category(
                    "— × tickets",
                    overwrites=overwrites
                )
            channel = await inter.guild.create_text_channel(
                name=f"ticket-{ticket_number}",
                category=category,
                overwrites=overwrites,
                topic=f"Создатель: {inter.user.id}"
            )
            fields = [
                {"name": "Создатель", "value": inter.user.mention, "inline": True},
                {"name": "Тема", "value": inter.text_values["ticket_title"], "inline": True},
                {"name": "Описание", "value": inter.text_values["ticket_description"], "inline": False}
            ]
            embed = make_embed(
                title=f"Тикет #{ticket_number}",
                description="🎫 Тикет создан",
                color=INFO_COLOR,
                fields=fields
            )
            view = TicketControls()
            await channel.send(embed=embed, view=view)
            await inter.followup.send(f"Тикет создан в канале {channel.mention}", ephemeral=True)
        except Exception as e:
            logger.error(f"Ошибка при создании тикета: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось создать тикет: {e}",
                color=ERROR_COLOR
            )
            await inter.followup.send(embed=embed, ephemeral=True)

    async def get_next_ticket_number(self, guild: disnake.Guild) -> int:
        existing = [c for c in guild.text_channels if c.name.startswith("ticket-")]
        numbers = [int(c.name.split("-", 1)[1]) for c in existing if c.name.split("-", 1)[1].isdigit()]
        return max(numbers, default=0) + 1

class TicketControls(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Закрыть", style=disnake.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        try:
            staff_role = inter.guild.get_role(STAFF_ROLE_ID)
            creator_id = int(inter.channel.topic.split(": ")[1]) if inter.channel.topic else None
            if not (inter.user.id == creator_id or (staff_role and staff_role in inter.user.roles)):
                embed = make_embed(
                    title="Ошибка",
                    description="У вас нет прав для закрытия этого тикета.",
                    color=ERROR_COLOR
                )
                await inter.response.send_message(embed=embed, ephemeral=True)
                return
            await inter.response.defer(ephemeral=True)
            await inter.followup.send("Тикет будет закрыт через 5 секунд...", ephemeral=True)
            await asyncio.sleep(5)
            await inter.channel.delete()
        except Exception as e:
            logger.error(f"Ошибка при закрытии тикета: {e}")
            await inter.followup.send("Не удалось закрыть тикет.", ephemeral=True)

class Tickets(commands.Cog):
    """Система тикетов для поддержки."""
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="setup-tickets",
        description="Отправляет сообщение для создания тикетов в текущий канал."
    )
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Команда для ручной отправки сообщения с кнопкой создания тикета."""
        try:
            embed = make_embed(
                title="🔥 Поддержка",
                description=(
                    "<:Sapphire_icon:1159787682734542869> Создав тикет, появляется ветка, где у вас появляются возможности:\n\n"
                    "• Пожаловаться на участника сервера.\n"
                    "• Задать какой-либо вопрос по серверу.\n"
                    "• Сообщить о найденных вами багах или недочётах.\n"
                    "• Предложить идею по улучшению сервера.\n\n"
                    "<:Sapphire_icon:1159787647712120924> За созданный вами тикет без причины вы получите предупреждение."
                ),
                color=INFO_COLOR
            )
            view = disnake.ui.View(timeout=None)
            view.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.danger,
                label="Открыть тикет!",
                emoji="📨",
                custom_id="create_ticket"
            ))
            await inter.channel.send(embed=embed, view=view)
            await inter.response.send_message("Сообщение для системы тикетов отправлено!", ephemeral=True)
        except Exception as e:
            logger.error(f"Ошибка при setup-tickets: {e}")
            await inter.response.send_message(f"Ошибка: {e}", ephemeral=True)

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "create_ticket":
            await inter.response.send_modal(TicketModal())


def setup(bot):
    bot.add_cog(Tickets(bot))
