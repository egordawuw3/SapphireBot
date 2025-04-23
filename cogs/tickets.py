import disnake
from disnake.ext import commands
from disnake import ButtonStyle, TextInputStyle
import asyncio

class TicketModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Тема тикета",
                placeholder="Кратко опишите тему обращения",
                custom_id="ticket_title",
                style=TextInputStyle.short,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Описание проблемы",
                placeholder="Подробно опишите вашу проблему или вопрос",
                custom_id="ticket_description",
                style=TextInputStyle.paragraph
            )
        ]
        super().__init__(
            title="Создание тикета",
            custom_id="ticket_modal",  # Убедитесь, что этот ID уникален для этого модального окна
            components=components
        )

    async def callback(self, inter: disnake.ModalInteraction):
        # Этот метод будет вызван автоматически при отправке модального окна
        try:
            # Получаем следующий номер тикета
            # Передаем self в get_next_ticket_number, так как это метод экземпляра
            ticket_number = await self.get_next_ticket_number(inter.guild)

            # Откладываем ответ, чтобы избежать ошибки "Interaction timed out"
            await inter.response.defer(ephemeral=True)

            # Создаем канал тикета
            overwrites = {
                inter.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                inter.user: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
                inter.guild.me: disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            # Добавляем права для роли Staff
            staff_role = disnake.utils.get(inter.guild.roles, name="Staff")
            if staff_role:
                overwrites[staff_role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

            # Добавляем права для роли по ID
            support_role = inter.guild.get_role(1207281299849744385)
            if support_role:
                overwrites[support_role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            else:
                print("Предупреждение: Роль support не найдена")

            category = disnake.utils.get(inter.guild.categories, name="— × tickets")
            if not category:
                category = await inter.guild.create_category(
                    "— × tickets",
                    overwrites=overwrites  # Применяем те же права к категории
                )

            channel = await inter.guild.create_text_channel(
                name=f"ticket-{ticket_number}",
                category=category,
                overwrites=overwrites,
                topic=f"Создатель: {inter.user.id}"  # Сохраняем ID создателя в описании канала
            )

            # Создаем эмбед для тикета
            embed = disnake.Embed(
                title=f"Тикет #{ticket_number}",
                description="🎫 Тикет создан",
                color=disnake.Color.blue()
            )
            embed.add_field(name="Создатель", value=inter.user.mention, inline=True)
            embed.add_field(name="Тема", value=inter.text_values["ticket_title"], inline=True)
            embed.add_field(name="Описание", value=inter.text_values["ticket_description"], inline=False)

            # Создаем кнопки управления
            view = TicketControls()

            # Отправляем сообщение в канал тикета
            await channel.send(embed=embed, view=view)

            # Отправляем отложенный ответ пользователю
            await inter.followup.send(
                f"Тикет создан в канале {channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            print(f"Ошибка в callback TicketModal: {e}") # Логируем ошибку для отладки
            # Обработка ошибок
            try:
                # Используем followup.send, так как ответ уже был отложен (defer)
                await inter.followup.send(
                    f"Произошла ошибка при создании тикета: {str(e)}",
                    ephemeral=True
                )
            except disnake.errors.InteractionNotResponded:
                 # Если взаимодействие уже неактивно, просто логируем
                 print(f"Не удалось отправить сообщение об ошибке пользователю {inter.user.id}, взаимодействие не отвечено.")
            except Exception as followup_e:
                 # Логируем любую другую ошибку при отправке сообщения об ошибке
                 print(f"Ошибка при отправке сообщения об ошибке пользователю {inter.user.id}: {followup_e}")


    async def get_next_ticket_number(self, guild):
        # Простая реализация - считаем существующие каналы
        # Убедимся, что считаем только текстовые каналы в категории "— × tickets" для точности
        category = disnake.utils.get(guild.categories, name="— × tickets")
        if not category:
            return 1 # Если категории нет, это первый тикет
        existing_tickets = len([c for c in category.text_channels if c.name.startswith("ticket-")])
        return existing_tickets + 1

class TicketControls(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Кнопки не должны исчезать

    @disnake.ui.button(label="Закрыть", style=ButtonStyle.red, emoji="🔒", custom_id="close_ticket_button")
    async def close_ticket(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        try:
            # Проверяем права на закрытие тикета
            staff_role = disnake.utils.get(inter.guild.roles, name="Staff")
            creator_id = int(inter.channel.topic.split(": ")[1]) if inter.channel.topic else None
            
            if not (inter.user.id == creator_id or (staff_role and staff_role in inter.user.roles)):
                await inter.response.send_message("У вас нет прав для закрытия этого тикета.", ephemeral=True)
                return

            await inter.response.defer(ephemeral=True)
            await inter.followup.send("Тикет будет закрыт через 5 секунд...", ephemeral=True)
            await asyncio.sleep(5)
            await inter.channel.delete()
            
        except Exception as e:
            print(f"Ошибка при закрытии тикета: {e}")
            await inter.followup.send("Не удалось закрыть тикет.", ephemeral=True)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Создаем задачу для отправки сообщения при запуске
        # Используем ensure_future для лучшей совместимости
        asyncio.ensure_future(self.setup_ticket_message())

    # Слушатель on_modal_submit УДАЛЕН, disnake обработает его автоматически

    async def setup_ticket_message(self):
        await self.bot.wait_until_ready()

        guild_id = 832291503581167636
        guild = self.bot.get_guild(guild_id)
        if not guild:
            print(f"Ошибка: Не удалось найти сервер с ID {guild_id}")
            return

        # Ищем канал по ID вместо имени
        support_channel = guild.get_channel(1054101394270978119)
        
        if not support_channel:
            print(f"Ошибка: Канал с ID 1054101394270978119 не найден")
            return

        # Очищаем все сообщения в канале
        try:
            async for message in support_channel.history(limit=None):
                await message.delete()
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Ошибка при очистке канала: {e}")
            return

        # Создаем эмбед для тикетов
        embed = disnake.Embed(
            title="🔥 Поддержка",
            description=(
                "<:Sapphire_icon:1159787682734542869> Создав тикет, появляется ветка, где у вас появляются возможности:\n\n"
                "• Пожаловаться на участника сервера.\n"
                "• Задать какой-либо вопрос по серверу.\n"
                "• Сообщить о найденных вами багах или недочётах.\n"
                "• Предложить идею по улучшению сервера.\n\n"
                "<:Sapphire_icon:1159787647712120924> За созданный вами тикет без причины вы получите предупреждение."
            ),
            color=disnake.Color.blue()
        ).set_image(
            url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif"
        )
        embed.set_footer(text="С уважением, администрация Sapphire Creators💎 ")

        # Создаем кнопку
        view = disnake.ui.View(timeout=None)
        view.add_item(disnake.ui.Button(
            style=ButtonStyle.danger,
            label="Открыть тикет!",
            emoji="📨",
            custom_id="create_ticket"
        ))

        # Удаляем старые сообщения с кнопкой создания тикета
        try:
            async for message in support_channel.history(limit=100):
                if message.author == self.bot.user and message.components:
                    for row in message.components:
                        for component in row.children:
                            if isinstance(component, disnake.ui.Button) and component.custom_id == "create_ticket":
                                await message.delete()
                                await asyncio.sleep(1)
        except Exception as e:
            print(f"Ошибка при удалении старых сообщений: {e}")

        # Отправляем новое сообщение
        try:
            await support_channel.send(embed=embed, view=view)
            print(f"Сообщение для создания тикетов отправлено в канал {channel_name}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")


    @commands.slash_command(
        name="setup-tickets",
        description="Отправляет сообщение для создания тикетов в текущий канал."
    )
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, inter: disnake.ApplicationCommandInteraction):
        """Команда для ручной отправки сообщения с кнопкой создания тикета."""
        embed = disnake.Embed(
            title="🎫 Поддержка",
            description=(
                "Создав тикет, появляется ветка, где у вас появляются возможности:\n\n"
                "• Пожаловаться на участника сервера.\n"
                "• Задать какой-либо вопрос по серверу.\n"
                "• Сообщить о найденных вами багах или недочётах.\n"
                "• Предложить идею по улучшению сервера.\n\n"
                "За созданный вами тикет без причины вы получите предупреждение."
            ),
            color=disnake.Color.blue()
        )
        embed.set_footer(text="Powered by Sapphire-Creators") # Обновленный футер

        # Используем постоянный View
        view = disnake.ui.View(timeout=None)
        view.add_item(disnake.ui.Button(
            style=ButtonStyle.danger,
            label="Открыть тикет!",
            emoji="📨",
            custom_id="create_ticket"
        ))

        try:
            await inter.channel.send(embed=embed, view=view)
            await inter.response.send_message("Сообщение для системы тикетов отправлено!", ephemeral=True)
        except disnake.errors.Forbidden:
             await inter.response.send_message("Ошибка: У бота нет прав на отправку сообщений в этом канале.", ephemeral=True)
        except Exception as e:
             print(f"Ошибка в команде setup_tickets: {e}")
             await inter.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        # Проверяем custom_id кнопки
        if inter.component.custom_id == "create_ticket":
            # Отправляем модальное окно
            await inter.response.send_modal(TicketModal())
        # Добавляем обработку кнопки закрытия тикета, если она не обрабатывается в View
        # elif inter.component.custom_id == "close_ticket_button":
        #     # Логика закрытия тикета (если не используется View класс)
        #     pass

# Функция setup для загрузки кога
def setup(bot):
    bot.add_cog(Tickets(bot))
