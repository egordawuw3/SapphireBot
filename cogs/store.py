import disnake
from disnake.ext import commands
from disnake import ButtonStyle, TextInputStyle
import asyncio

class StoreModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Что вы хотите заказать?",
                placeholder="Монтаж, дизайн и т.п.",
                custom_id="service_name",
                style=TextInputStyle.short,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Подробное описание заказа",
                placeholder="Опишите детально, что именно вы хотите заказать",
                custom_id="service_description",
                style=TextInputStyle.paragraph
            )
        ]
        super().__init__(
            title="Заказ услуги",
            custom_id="store_modal",
            components=components
        )

    async def callback(self, inter: disnake.ModalInteraction):
        try:
            await inter.response.defer(ephemeral=True)

            # Создаем канал заказа
            overwrites = {
                inter.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                inter.user: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
                inter.guild.me: disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            # Добавляем права для роли Staff
            staff_role = disnake.utils.get(inter.guild.roles, name="Staff")
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

            # Создаем эмбед для заказа
            embed = disnake.Embed(
                title="💎 Новый заказ",
                description="Заказ создан и ожидает обработки",
                color=disnake.Color.blue()
            )
            embed.add_field(name="Заказчик", value=inter.user.mention, inline=True)
            embed.add_field(name="Услуга", value=inter.text_values["service_name"], inline=True)
            embed.add_field(name="Описание", value=inter.text_values["service_description"], inline=False)

            # Создаем кнопки управления
            view = StoreControls()

            # Отправляем сообщение в канал заказа
            await channel.send(embed=embed, view=view)

            await inter.followup.send(
                f"Заказ создан в канале {channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            print(f"Ошибка при создании заказа: {e}")
            await inter.followup.send(
                "Произошла ошибка при создании заказа. Пожалуйста, попробуйте позже.",
                ephemeral=True
            )

class StoreControls(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Закрыть", style=ButtonStyle.red, emoji="🔒", custom_id="close_order")
    async def close_order(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        try:
            staff_role = disnake.utils.get(inter.guild.roles, name="Staff")
            creator_id = int(inter.channel.topic.split(": ")[1]) if inter.channel.topic else None
            
            if not (inter.user.id == creator_id or (staff_role and staff_role in inter.user.roles)):
                await inter.response.send_message("У вас нет прав для закрытия этого заказа.", ephemeral=True)
                return

            await inter.response.defer(ephemeral=True)
            await inter.followup.send("Заказ будет закрыт через 5 секунд...", ephemeral=True)
            await asyncio.sleep(5)
            await inter.channel.delete()
            
        except Exception as e:
            print(f"Ошибка при закрытии заказа: {e}")
            await inter.followup.send("Не удалось закрыть заказ.", ephemeral=True)

class Store(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        asyncio.ensure_future(self.setup_store_message())

    async def setup_store_message(self):
        await self.bot.wait_until_ready()

        guild_id = 832291503581167636
        guild = self.bot.get_guild(guild_id)
        if not guild:
            print(f"Ошибка: Не удалось найти сервер с ID {guild_id}")
            return

        # Только store channel
        store_channel = disnake.utils.get(guild.text_channels, name="📦・store")
        
        if store_channel:
            try:
                # Удаляем ВСЕ сообщения бота в канале
                async for message in store_channel.history(limit=None):
                    if message.author == self.bot.user:
                        await message.delete()
                        await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Ошибка при очистке store-канала: {e}")

            # Создаем и отправляем новое сообщение
            embed = disnake.Embed(
                title="💎 Заказать услугу",
                description=(
                    "> <:Sapphire__icon:1159785635628994601> Для быстрого взаимодействия с меню, используйте кнопку ЗАКАЗАТЬ.\n\n"
                    "> <:Sapphire_icon:1159787682734542869> Если бот не работает, напишите в ЛС @w1nchester0111."
                ),
                color=disnake.Color.blue()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif?ex=6809cba9&is=68087a29&hm=f558c4ed18566a404275a62081737ba50c9342a73fe5169f812f1512e00c412f&")

            view = disnake.ui.View(timeout=None)
            view.add_item(disnake.ui.Button(
                style=ButtonStyle.danger,
                label="⚡ЗАКАЗАТЬ",
                custom_id="create_order"
            ))

            try:
                await store_channel.send(embed=embed, view=view)
                print(f"Новое сообщение отправлено в store-канал")
            except Exception as e:
                print(f"Ошибка при отправке: {e}")

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "create_order":
            await inter.response.send_modal(StoreModal())

def setup(bot):
    bot.add_cog(Store(bot))