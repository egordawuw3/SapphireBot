import disnake
from disnake.ext import commands
import asyncio
import logging
from utils.embed_utils import make_embed
from config.constants import STAFF_ROLE_ID, INFO_COLOR, ERROR_COLOR, SUCCESS_COLOR

logger = logging.getLogger(__name__)

class StoreModal(disnake.ui.Modal):
    """Модальное окно для заказа услуги."""
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Что вы хотите заказать?",
                custom_id="service_name",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Подробное описание заказа",
                custom_id="service_description",
                style=disnake.TextInputStyle.paragraph
            )
        ]
        super().__init__(
            title="Заказ услуги",
            custom_id="store_modal",
            components=components
        )

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        try:
            await inter.response.defer(ephemeral=True)
            overwrites = {
                inter.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                inter.user: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
                inter.guild.me: disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            staff_role = inter.guild.get_role(STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            category = disnake.utils.get(inter.guild.categories, name="— × store")
            if not category:
                category = await inter.guild.create_category(
                    "— × store",
                    overwrites=overwrites
                )
            channel = await inter.guild.create_text_channel(
                name=f"order-{inter.user.name}",
                category=category,
                overwrites=overwrites,
                topic=f"Заказчик: {inter.user.id}"
            )
            fields = [
                {"name": "Заказчик", "value": inter.user.mention, "inline": True},
                {"name": "Услуга", "value": inter.text_values["service_name"], "inline": True},
                {"name": "Описание", "value": inter.text_values["service_description"], "inline": False}
            ]
            embed = make_embed(
                title="💎 Новый заказ",
                description="Заказ создан и ожидает обработки",
                color=INFO_COLOR,
                fields=fields
            )
            view = StoreControls()
            await channel.send(embed=embed, view=view)
            await inter.followup.send(
                f"Заказ создан в канале {channel.mention}",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {e}")
            embed = make_embed(
                title="Ошибка",
                description="Произошла ошибка при создании заказа. Пожалуйста, попробуйте позже.",
                color=ERROR_COLOR
            )
            await inter.followup.send(embed=embed, ephemeral=True)

class StoreControls(disnake.ui.View):
    """Кнопки управления заказом."""
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Закрыть", style=disnake.ButtonStyle.red, emoji="🔒", custom_id="close_order")
    async def close_order(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        try:
            staff_role = inter.guild.get_role(STAFF_ROLE_ID)
            creator_id = int(inter.channel.topic.split(": ")[1]) if inter.channel.topic else None
            if not (inter.user.id == creator_id or (staff_role and staff_role in inter.user.roles)):
                embed = make_embed(
                    title="Ошибка",
                    description="У вас нет прав для закрытия этого заказа.",
                    color=ERROR_COLOR
                )
                await inter.response.send_message(embed=embed, ephemeral=True)
                return
            await inter.response.defer(ephemeral=True)
            await inter.followup.send("Заказ будет закрыт через 5 секунд...", ephemeral=True)
            await asyncio.sleep(5)
            await inter.channel.delete()
        except Exception as e:
            logger.error(f"Ошибка при закрытии заказа: {e}")
            await inter.followup.send("Не удалось закрыть заказ.", ephemeral=True)

class Store(commands.Cog):
    """Cog для системы заказов услуг."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        asyncio.ensure_future(self.setup_store_message())

    async def setup_store_message(self) -> None:
        await self.bot.wait_until_ready()
        guild_id = 832291503581167636
        guild = self.bot.get_guild(guild_id)
        if not guild:
            logger.error(f"Ошибка: Не удалось найти сервер с ID {guild_id}")
            return
        store_channel = disnake.utils.get(guild.text_channels, name="📦・store")
        if store_channel:
            try:
                async for message in store_channel.history(limit=None):
                    if message.author == self.bot.user:
                        await message.delete()
                        await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Ошибка при очистке store-канала: {e}")
            embed = make_embed(
                title="💎 Заказать услугу",
                description=(
                    "> <:Sapphire__icon:1159785635628994601> Для быстрого взаимодействия с меню, используйте кнопку ЗАКАЗАТЬ.\n\n"
                    "> <:Sapphire_icon:1159787682734542869> Если бот не работает, напишите в ЛС @w1nchester0111."
                ),
                color=INFO_COLOR
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif?")
            view = disnake.ui.View(timeout=None)
            view.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.danger,
                label="⚡ЗАКАЗАТЬ",
                custom_id="create_order"
            ))
            try:
                await store_channel.send(embed=embed, view=view)
                logger.info(f"Новое сообщение отправлено в store-канал")
            except Exception as e:
                logger.error(f"Ошибка при отправке: {e}")

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "create_order":
            await inter.response.send_modal(StoreModal())

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Store(bot))